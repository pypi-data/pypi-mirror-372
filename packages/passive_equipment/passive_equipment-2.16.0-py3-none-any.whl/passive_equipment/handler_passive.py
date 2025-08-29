# pylint: skip-file
"""设备服务端处理器."""
import csv
import json
import logging
import os
import pathlib
import subprocess
import threading
import time
import socket
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Union, Optional, Callable

from inovance_tag.tag_communication import TagCommunication
from mitsubishi_plc.mitsubishi_plc import MitsubishiPlc
from modbus_api.modbus_api import ModbusApi
from mysql_api.mysql_database import MySQLDatabase
from secsgem.common import DeviceType
from secsgem.gem import CollectionEvent, GemEquipmentHandler, StatusVariable, RemoteCommand, Alarm, DataValue, \
    EquipmentConstant
from secsgem.secs.data_items.tiack import TIACK
from secsgem.secs.functions import SecsS02F18
from secsgem.secs.variables import U4
from secsgem.hsms import HsmsSettings, HsmsConnectMode
from siemens_plc.s7_plc import S7PLC
from socket_cyg.socket_server_asyncio import CygSocketServerAsyncio

from passive_equipment.enum_sece_data_type import EnumSecsDataType
from passive_equipment.handler_config import HandlerConfig
from passive_equipment.thread_methods import ThreadMethods


class HandlerPassive(GemEquipmentHandler):
    """Passive equipment handler class."""

    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"

    def __init__(self, module_path: str, control_instance_dict: dict, open_flag: bool = False, **kwargs):
        """HandlerPassive 构造函数.

        Args:
            module_path: module 路径.
            control_instance_dict: 下位机控制实例字典.
            open_flag: 是否打开监控下位机的线程.
            **kwargs: 关键字参数.
        """
        logging.basicConfig(level=logging.INFO, encoding="UTF-8", format=self.LOG_FORMAT)

        self.control_instance_dict = control_instance_dict

        self._module_path = module_path
        self._kwargs = kwargs
        self._open_flag = open_flag  # 是否打开监控下位机的线程
        self._file_handler = None  # 保存日志的处理器
        self._mysql = None  # 数据库实例对象

        self.logger = logging.getLogger(__name__)  # handler_passive 日志器

        self.config_instance = HandlerConfig(self._get_config_path())  # 配置文件实例对象
        self.config = self.config_instance.config_data

        hsms_settings = HsmsSettings(
            address=self.config["secs_conf"].get("secs_ip", "127.0.0.1"),
            port=self.config["secs_conf"].get("secs_port", 5000),
            connect_mode=getattr(HsmsConnectMode, "PASSIVE"),
            device_type=DeviceType.EQUIPMENT
        )  # high speed message server 配置

        super().__init__(settings=hsms_settings)
        self.model_name = self.config["secs_conf"].get("model_name", "CYG SECSGEM")
        self.software_version = self.config["secs_conf"].get("software_version", "1.0.0")
        self.recipes = self.config.get("all_recipe", {})  # 获取所有上传过的配方信息
        self.alarm_id = U4(0)  # 保存报警id
        self.alarm_text = ""  # 保存报警内容

        self._initial_evnet()
        self._initial_status_variable()
        self._initial_data_value()
        self._initial_equipment_constant()
        self._initial_remote_command()
        self._initial_alarm()
        self._initial_log_config()

        self.thread_methods = ThreadMethods(self)

        self.enable_mes()  # 启动设备端服务器
        self._monitor_control_thread()

    def _monitor_control_thread(self):
        """监控下位机的线程."""
        for control_name, control_instance in self.control_instance_dict.items():
            control_type = control_name.split("_")[-1]
            if self._open_flag:
                self.logger.info("打开监控下位机的线程.")
                if isinstance(control_instance, CygSocketServerAsyncio):
                    self.logger.info("下位机是 Socket")
                    self.__start_monitor_socket_thread(control_instance, self.operate_func_socket)
                else:
                    if control_instance.communication_open():
                        self.logger.info("首次连接 %s 下位机成功, ip: %s", control_type, control_instance.ip)
                    else:
                        self.logger.info("首次连接 %s 下位机失败, ip: %s", control_type, control_instance.ip)
                    self.__start_monitor_plc_thread(control_instance, control_name)
            else:
                self.logger.info("不打开监控下位机的线程.")

    def __start_monitor_socket_thread(self, control_instance: CygSocketServerAsyncio, func: Callable):
        """启动供下位机连接的socket服务.

        Args:
            control_instance: CygSocketServerAsyncio 实例.
            func: 执行操作的函数.
        """
        control_instance.operations_return_data = func

        threading.Thread(target=self.thread_methods.run_socket_server, args=(control_instance,), daemon=True).start()

    def __start_monitor_plc_thread(self, plc: Union[S7PLC, TagCommunication, MitsubishiPlc, ModbusApi], control_name: str):
        """启动监控 plc 的线程.

        Args:
            plc: plc 实例对象.
            control_name: 设备名称.
        """
        threading.Thread(target=self.thread_methods.mes_heart, args=(plc, control_name,), daemon=True).start()
        threading.Thread(target=self.thread_methods.control_state, args=(plc, control_name,), daemon=True).start()
        threading.Thread(target=self.thread_methods.machine_state, args=(plc, control_name,), daemon=True).start()
        for signal_name, signal_info in self.config["signal_address"][control_name].items():
            if signal_info.get("loop", False):  # 实时监控的信号才会创建线程
                threading.Thread(
                    target=self.thread_methods.monitor_plc_address, daemon=True,
                    args=(plc, signal_name, control_name,),
                    name=signal_name
                ).start()

    @property
    def mysql(self) -> MySQLDatabase:
        """数据库实例对象.

        Returns:
            MySQLDatabase: 返回操作 Mysql 数据的实例对象.
        """
        if self._mysql:
            return self._mysql
        self._mysql = MySQLDatabase(
            self.get_ec_value_with_name("mysql_user_name"),
            self.get_ec_value_with_name("mysql_password"),
            host=self.get_ec_value_with_name("mysql_host")
        )
        return self._mysql

    @mysql.setter
    def mysql(self, value: MySQLDatabase):
        """设置数据库实例对象.

        Args:
            value: 数据库 MySQLDatabase实例.
        """
        if not isinstance(value, MySQLDatabase) and value is not None:
            raise ValueError("mysql 必须是一个 MySQLDatabase 实例或 None")
        self._mysql = value

    @property
    def file_handler(self) -> TimedRotatingFileHandler:
        """设置保存日志的处理器, 每隔 24h 自动生成一个日志文件.

        Returns:
            TimedRotatingFileHandler: 返回 TimedRotatingFileHandler 日志处理器.
        """
        if self._file_handler is None:
            self._file_handler = TimedRotatingFileHandler(
                f"{os.getcwd()}/log/all.log",
                when="D", interval=1, backupCount=10, encoding="UTF-8"
            )
            self._file_handler.namer = self._custom_log_name
            self._file_handler.setFormatter(logging.Formatter(self.LOG_FORMAT))
        return self._file_handler

    @staticmethod
    def _custom_log_name(log_path: str):
        """自定义新生成的日志名称.

        Args:
            log_path: 原始的日志文件路径.

        Returns:
            str: 新生成的自定义日志文件路径.
        """
        _, suffix, date_str, *__ = log_path.split(".")
        new_log_path = f"{os.getcwd()}/log/all_{date_str}.{suffix}"
        return new_log_path

    @staticmethod
    def _create_log_dir():
        """判断log目录是否存在, 不存在就创建."""
        log_dir = pathlib.Path(f"{os.getcwd()}/log")
        if not log_dir.exists():
            os.mkdir(log_dir)

    @staticmethod
    def _get_alarm_path() -> Optional[str]:
        """获取报警表格的路径.

        Returns:
            Optional[str]: 返回报警表格路径, 不存在返回None.
        """
        alarm_path = os.path.join(os.getcwd(), "alarm.csv")
        if os.path.exists(alarm_path):
            return alarm_path
        return None

    @staticmethod
    def send_data_to_socket_server(ip: str, port: int, data: str):
        """向服务端发送数据.

        Args:
            ip: Socket 服务端 ip.
            port: Socket 服务端 port.
            data: 要发送的数据.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.sendall(data.encode("UTF-8"))

    def _initial_log_config(self) -> None:
        """日志配置."""
        self._create_log_dir()
        self.protocol.communication_logger.addHandler(self.file_handler)  # secs 日志保存到统一文件
        self.logger.addHandler(self.file_handler)  # handler_passive 日志保存到统一文件
        if self.get_ec_value_with_name("whether_have_database"):
            self.mysql.logger.addHandler(self.file_handler)
        for _, control_instance in self.control_instance_dict.items():
            control_instance.logger.addHandler(self.file_handler)

    def _initial_evnet(self):
        """加载定义好的事件."""
        collection_events = self.config.get("collection_events", {})
        for event_name, event_info in collection_events.items():
            self.collection_events.update({
                event_name: CollectionEvent(name=event_name, data_values=[], **event_info)
            })

    def _initial_status_variable(self):
        """加载定义好的变量."""
        status_variables = self.config.get("status_variable", {})
        for sv_name, sv_info in status_variables.items():
            sv_id = sv_info.get("svid")
            value_type_str = sv_info.get("value_type")
            value_type = getattr(EnumSecsDataType, value_type_str).value
            sv_info["value_type"] = value_type
            self.status_variables.update({sv_id: StatusVariable(name=sv_name, **sv_info)})
            sv_info["value_type"] = value_type_str

    def _initial_data_value(self):
        """加载定义好的 data value."""
        data_values = self.config.get("data_values", {})
        for data_name, data_info in data_values.items():
            data_id = data_info.get("dvid")
            value_type_str = data_info.get("value_type")
            value_type = getattr(EnumSecsDataType, value_type_str).value
            data_info["value_type"] = value_type
            self.data_values.update({data_id: DataValue(name=data_name, **data_info)})
            data_info["value_type"] = value_type_str

    def _initial_equipment_constant(self):
        """加载定义好的常量."""
        equipment_constants = self.config.get("equipment_constant", {})
        for ec_name, ec_info in equipment_constants.items():
            ec_id = ec_info.get("ecid")
            value_type_str = ec_info.get("value_type")
            value_type = getattr(EnumSecsDataType, value_type_str).value
            ec_info["value_type"] = value_type
            ec_info.update({"min_value": 0, "max_value": 0})
            self.equipment_constants.update({ec_id: EquipmentConstant(name=ec_name, **ec_info)})
            ec_info["value_type"] = value_type_str

    def _initial_remote_command(self):
        """加载定义好的远程命令."""
        remote_commands = self.config.get("remote_commands", {})
        for rc_name, rc_info in remote_commands.items():
            ce_id = rc_info.get("ce_id")
            self.remote_commands.update({rc_name: RemoteCommand(name=rc_name, ce_finished=ce_id, **rc_info)})

    def _initial_alarm(self):
        """加载定义好的报警."""
        if alarm_path := self._get_alarm_path():
            with pathlib.Path(alarm_path).open("r+") as file:  # pylint: disable=W1514
                csv_reader = csv.reader(file)
                next(csv_reader)
                for row in csv_reader:
                    alarm_id, alarm_name, alarm_text, alarm_code, ce_on, ce_off, *_ = row
                    self.alarms.update({
                        alarm_id: Alarm(alarm_id, alarm_name, alarm_text, int(alarm_code), ce_on, ce_off)
                    })

    def enable_mes(self):
        """启动 EAP 连接的 MES服务."""
        self.enable()  # 设备和host通讯
        self.logger.info("Passive 服务已启动, 地址: %s %s!", self.settings.address, self.settings.port)

    def _get_config_path(self) -> str:
        """获取配置文件绝对路径."""
        config_file_path = self._module_path.replace(".py", ".json")
        self.logger.info("配置文件路径: %s", config_file_path)
        return config_file_path

    def _get_sv_id_with_name(self, sv_name: str) -> Optional[int]:
        """根据变量名获取变量id.

        Args:
            sv_name: 变量名称.

        Returns:
            Optional[int]: 返回变量id, 没有此变量返回None.
        """
        if sv_info := self.config_instance.get_config_value(sv_name, parent_name="status_variable"):
            return sv_info["svid"]
        return None

    def _get_dv_id_with_name(self, dv_name: str) -> Optional[int]:
        """根据data名获取data id.

        Args:
            dv_name: 变量名称.

        Returns:
            Optional[int]: 返回data id, 没有此data返回None.
        """
        if sv_info := self.config_instance.get_config_value("data_values").get(dv_name):
            return sv_info["dvid"]
        return None

    def _get_ec_id_with_name(self, ec_name: str) -> Optional[int]:
        """根据常量名获取常量 id.

        Args:
            ec_name: 常量名称.

        Returns:
            Optional[int]: 返回常量 id, 没有此常量返回None.
        """
        if ec_info := self.config_instance.get_config_value("equipment_constant").get(ec_name):
            return ec_info["ecid"]
        return None

    def set_sv_value_with_name(self, sv_name: str, sv_value: Union[str, int, float, list], is_save: bool = False):
        """设置指定 sv 变量的值.

        Args:
            sv_name (str): 变量名称.
            sv_value (Union[str, int, float, list]): 要设定的值.
            is_save: 是否更新配置文件, 默认不更新.
        """
        self.logger.info("设置 sv 值, %s = %s", sv_name, sv_value)
        self.status_variables.get(self._get_sv_id_with_name(sv_name)).value = sv_value
        if is_save:
            self.config_instance.update_config_sv_value(sv_name, sv_value)

    def set_dv_value_with_name(self, dv_name: str, dv_value: Union[str, int, float, list], is_save: bool = False):
        """设置指定 dv 变量的值.

        Args:
            dv_name: dv 变量名称.
            dv_value: 要设定的值.
            is_save: 是否更新配置文件, 默认不更新.
        """
        self.logger.info("设置 dv 值, %s = %s", dv_name, dv_value)
        self.data_values.get(self._get_dv_id_with_name(dv_name)).value = dv_value
        if is_save:
            self.config_instance.update_config_dv_value(dv_name, dv_value)

    def set_ec_value_with_name(self, ec_name: str, ec_value: Union[str, int, float]):
        """设置指定 ec 变量的值.

        Args:
            ec_name (str): ec 变量名称.
            ec_value (Union[str, int, float]): 要设定的 ec 的值.
        """
        self.logger.info("设置 ec 值, %s = %s", ec_name, ec_value)
        self.equipment_constants.get(self._get_ec_id_with_name(ec_name)).value = ec_value

    def get_sv_value_with_name(self, sv_name: str, save_log: bool = True) -> Union[int, str, bool, list, float]:
        """根据变量 sv 名获取变量 sv 值.

        Args:
            sv_name: 变量名称.
            save_log: 是否保存日志, 默认保存.

        Returns:
            Union[int, str, bool, list, float]: 返回对应变量的值.
        """
        if sv_instance := self.status_variables.get(self._get_sv_id_with_name(sv_name)):
            sv_value = sv_instance.value
            if save_log:
                self.logger.info("当前 sv %s = %s", sv_name, sv_value)
            return sv_instance.value
        return None

    def get_dv_value_with_name(self, dv_name: str, save_log: bool = True) -> Union[int, str, bool, list, float]:
        """根据变量 dv 名获取变量 dv 值..

        Args:
            dv_name: dv 名称.
            save_log: 是否吓死日志, 默认保存.

        Returns:
            Union[int, str, bool, list, float]: 返回对应 dv 变量的值.
        """
        if dv_instance := self.data_values.get(self._get_dv_id_with_name(dv_name)):
            dv_value = dv_instance.value
            if save_log:
                self.logger.info("当前 dv %s = %s", dv_name, dv_value)
            return dv_value
        return None

    def get_ec_value_with_name(self, ec_name: str, save_log: bool = True) -> Union[int, str, bool, list, float]:
        """根据常量名获取常量值.

        Args:
            ec_name: 常量名称.
            save_log: 是否吓死日志, 默认保存.

        Returns:
            Union[int, str, bool, list, float]: 返回对应常量的值.
        """
        if ec_instance := self.equipment_constants.get(self._get_ec_id_with_name(ec_name)):
            ec_value = ec_instance.value
            if save_log:
                self.logger.info("当前 ec %s = %s", ec_name, ec_value)
            return ec_value
        return None

    def send_s6f11(self, event_name: str):
        """给EAP发送S6F11事件.

        Args:
            event_name: 事件名称.
        """
        threading.Thread(target=self.thread_methods.collection_event_sender, args=(event_name,), daemon=True).start()

    def set_clear_alarm(self, alarm_code: int, plc: Union[S7PLC, TagCommunication, MitsubishiPlc, ModbusApi], equipment_name):
        """通过S5F1发送报警和解除报警.

        Args:
            alarm_code: 报警 code, 128: 报警, 0: 清除报警.
            plc: plc 实例.
            equipment_name: 设备名称.
        """
        address_info = self.config_instance.get_signal_address_info("alarm_id", equipment_name)
        if alarm_code == self.get_ec_value_with_name("occur_alarm_code"):
            alarm_id = plc.execute_read(**address_info, save_log=False)
            self.logger.info("出现报警, 报警id: %s", alarm_id)
            try:
                self.alarm_id = U4(alarm_id)
                if alarm_instance := self.alarms.get(str(alarm_id)):
                    self.alarm_text = alarm_instance.text
                else:
                    self.alarm_text = "Alarm is not defined."
            except ValueError:
                self.logger.warning("报警id非法, 报警id: %s")
                self.alarm_id = U4(0)
                self.alarm_text = "Alarm is not defined."

        threading.Thread(target=self.thread_methods.alarm_sender, args=(alarm_code,), daemon=True).start()

    def set_clear_alarm_socket(self, alarm_code: int, alarm_id: int, alarm_text: str):
        """通过S5F1发送报警和解除报警.

        Args:
            alarm_code: 报警 code, 128: 报警, 0: 清除报警.
            alarm_id: 报警 id.
            alarm_text: 报警内容.
        """
        self.alarm_id = U4(int(alarm_id))
        self.alarm_text = alarm_text
        threading.Thread(target=self.thread_methods.alarm_sender, args=(alarm_code,), daemon=True).start()

    def get_signal_to_sequence(self, signal_name: str, equipment_name: str):
        """监控到信号执行 call_backs.

        Args:
            signal_name: 信号名称.
            equipment_name: 设备名称.
        """
        _ = "=" * 40
        self.logger.info("%s 监控到 %s 设备的 %s 信号 %s", _, equipment_name, signal_name, _)
        self.execute_call_backs(self.config_instance.get_call_backs(signal_name, equipment_name), equipment_name)
        self.logger.info("%s %s 结束 %s", _, signal_name, _)
        self.logger.info("")

    def execute_call_backs(self, call_backs: list, equipment_name: str):
        """根据操作列表执行具体的操作.

        Args:
            call_backs: 要执行动作的信息列表, 按照列表顺序执行.
            equipment_name: 设备名称.
        """
        for i, call_back in enumerate(call_backs, 1):
            description = call_back.get("description")
            self.logger.info("%s 第 %s 步: %s %s", "-" * 30, i, description, "-" * 30)
            operation_func = getattr(self, call_back.get(f"operation_func"))
            operation_func(call_back=call_back, equipment_name=equipment_name)
            self._is_send_event(call_back.get("event_name"))
            self.logger.info("%s %s 结束 %s", "-" * 30, description, "-" * 30)

    def update_dv_specify_value(self, call_back: dict, **kwargs):
        """更新 dv 指定值.

        Args:
            call_back: 要执行的 call_back 信息.
        """
        value = call_back.get("value")
        dv_name = call_back.get("dv_name")
        self.set_dv_value_with_name(dv_name, value)
        self.logger.info("当前 %s 值: %s", dv_name, value)

    def update_sv_specify_value(self, call_back: dict, **kwargs):
        """更新 sv 指定值.

        Args:
            call_back: 要执行的 call_back 信息.
        """
        value = call_back.get("value")
        sv_name = call_back.get("sv_name")
        self.set_sv_value_with_name(sv_name, value)
        self.logger.info("当前 %s 值: %s", sv_name, value)

    def read_update_sv(self, call_back: dict, equipment_name: str):
        """读取 plc 数据更新 sv 值.

        Args:
            call_back: 要执行的 call_back 信息.
            equipment_name: 设备名称.
        """
        plc = self.control_instance_dict.get(equipment_name)
        sv_name = call_back.get("sv_name")
        address_info = self.config_instance.get_call_back_address_info(call_back, equipment_name)
        plc_value = plc.execute_read(**address_info)
        self.set_sv_value_with_name(sv_name, plc_value)
        self.logger.info("当前 %s 值: %s", sv_name, plc_value)

    def read_update_dv(self, call_back: dict, equipment_name: str):
        """读取 plc 数据更新 dv 值.

        Args:
            call_back: 要执行的 call_back 信息.
            equipment_name: 设备名称.

        """
        plc = self.control_instance_dict.get(equipment_name)
        dv_name = call_back.get("dv_name")
        address_info = self.config_instance.get_call_back_address_info(call_back, equipment_name)
        plc_value = plc.execute_read(**address_info)
        if scale := call_back.get("scale"):
            plc_value = round(plc_value / scale, 3)
        self.set_dv_value_with_name(dv_name, plc_value)
        self.logger.info("当前 %s 值: %s", dv_name, plc_value)

    def read_multiple_update_dv_snap7(self, call_back: dict, equipment_name: str):
        """读取 Snap7 plc 多个数据更新 dv 值.

        Args:
            call_back: 要执行的 call_back 信息.
            equipment_name: 设备名称.

        """
        plc = self.control_instance_dict.get(equipment_name)
        value_list = []
        count_num = call_back["count_num"]
        gap = call_back.get("gap", 1)
        start_address = call_back.get("address")
        for i in range(count_num):
            address_info = {
                "address": start_address + i * gap,
                "data_type": call_back.get("data_type"),
                "db_num": self.get_ec_value_with_name("db_num"),
                "size": call_back.get("size", 1),
                "bit_index": call_back.get("bit_index", 0)
            }
            plc_value = plc.execute_read(**address_info)
            value_list.append(plc_value)
        self.set_dv_value_with_name(call_back.get("dv_name"), value_list)
        self.logger.info("当前 dv %s 值 %s", call_back.get("dv_name"), value_list)

    def read_multiple_update_dv_tag(self, call_back: dict, equipment_name: str):
        """读取标签通讯 plc 多个数据更新 dv 值.

        Args:
            call_back: 要执行的 call_back 信息.
            equipment_name: 设备名称。
        """
        plc = self.control_instance_dict.get(equipment_name)
        value_list = []
        count_num = call_back["count_num"]
        start_address = call_back.get("address")
        for i in range(1, count_num + 1):
            address_info = {
                "address": start_address.replace("$", str(i)),
                "data_type": call_back.get("data_type"),
            }
            plc_value = plc.execute_read(**address_info)
            value_list.append(plc_value)
        self.set_dv_value_with_name(call_back.get("dv_name"), value_list)
        self.logger.info("当前 dv %s 值 %s", call_back.get("dv_name"), value_list)

    def read_multiple_update_dv_modbus(self, call_back: dict, equipment_name: str):
        """读取 modbus 通讯 plc 多个数据更新 dv 值.

        Args:
            call_back: 要执行的 call_back 信息.
            equipment_name: 设备名称。
        """
        plc = self.control_instance_dict.get(equipment_name)
        value_list = []
        count_num = call_back["count_num"]
        start_address = call_back.get("address")
        size = call_back.get("size")
        for i in range(count_num):
            address_info = {
                "address": start_address + i * size,
                "data_type": call_back.get("data_type"),
                "size": size
            }
            plc_value = plc.execute_read(**address_info)
            value_list.append(plc_value)
        self.set_dv_value_with_name(call_back.get("dv_name"), value_list)
        self.logger.info("当前 dv %s 值 %s", call_back.get("dv_name"), value_list)

    def write_multiple_dv_value_snap7(self, call_back: dict, equipment_name):
        """向 snap7 plc 地址写入 dv 值.

        Args:
            call_back: 要执行的 call_back 信息.
            equipment_name: 设备名称.
        """
        value_list = self.get_dv_value_with_name(call_back.get("dv_name"))
        gap = call_back.get("gap", 1)
        for i, value in enumerate(value_list):
            _call_back = {
                "address": call_back.get("address") + gap * i,
                "data_type": call_back.get("data_type"),
                "db_num": self.get_ec_value_with_name("db_num"),
                "size": call_back.get("size", 2),
                "bit_index": call_back.get("bit_index", 0)
            }
            self._write_value(_call_back, value, equipment_name)

    def write_multiple_dv_value_tag(self, call_back: dict, equipment_name: str):
        """向标签通讯 plc 地址写入 dv 值.

        Args:
            call_back: 要执行的 call_back 信息.
            equipment_name: 设备名称.
        """
        value_list = self.get_dv_value_with_name(call_back.get("dv_name"))
        for i, value in enumerate(value_list, 1):
            _call_back = {
                "address": call_back.get("address").replace("$", str(i)),
                "data_type": call_back.get("data_type"),
            }
            self._write_value(_call_back, value, equipment_name)

    def write_multiple_dv_value_modbus(self, call_back: dict, equipment_name: str):
        """向 modbus 通讯 plc 地址写入 dv 值.

        Args:
            call_back: 要执行的 call_back 信息.
            equipment_name: 设备名称.
        """
        value_list = self.get_dv_value_with_name(call_back.get("dv_name"))
        start_address = call_back.get("address")
        size = call_back.get("size")
        for i, value in enumerate(value_list, 0):
            _call_back = {
                "address": start_address + i * size,
                "data_type": call_back.get("data_type"),
            }
            self._write_value(_call_back, value, equipment_name)

    def write_sv_value(self, call_back: dict, equipment_name: str):
        """向 plc 地址写入 sv 值.

        Args:
            call_back: 要执行的 call_back 信息.
            equipment_name: 设备名称.
        """
        sv_value = self.get_sv_value_with_name(call_back.get("sv_name"))
        self._write_value(call_back, sv_value, equipment_name)

    def write_dv_value(self, call_back: dict, equipment_name: str):
        """向 plc 地址写入 dv 值.

        Args:
            call_back: 要执行的 call_back 信息.
            equipment_name: 设备名称.
        """
        dv_value = self.get_dv_value_with_name(call_back.get("dv_name"))
        self._write_value(call_back, dv_value, equipment_name)

    def write_specify_value(self, call_back: dict, equipment_name: str):
        """向 plc 地址写入指定值.

        Args:
            call_back: 要执行的 call_back 信息.
            equipment_name: 设备名称.
        """
        value = call_back.get("value")
        self._write_value(call_back, value, equipment_name)

    def _write_value(self, call_back: dict, value: Union[int, float, bool, str], equipment_name: str):
        """向 snap7 plc 地址写入指定值.

        Args:
            call_back: 要执行的 call_back 信息.
            value: 要写入的值.
            equipment_name: 设备名称.
        """
        # 如果有前提条件, 要先判断前提条件再写入
        plc = self.control_instance_dict.get(equipment_name)

        if call_back.get("premise_address"):
            premise_value = call_back.get("premise_value")
            wait_time = call_back.get("wait_time", 600000)
            address_info = self.config_instance.get_call_back_address_info(call_back, equipment_name, True)
            while plc.execute_read(**address_info) != premise_value:
                self.logger.info("%s 前提条件值 != %s", call_back.get("description"), call_back.get("premise_value"))
                self.wait_time(1)
                wait_time -= 1
                if wait_time == 0:
                    break

        address_info = self.config_instance.get_call_back_address_info(call_back, equipment_name, False)
        plc.execute_write(**address_info, value=value)
        if isinstance(plc, S7PLC) and address_info.get("data_type") == "bool":
            self.confirm_write_success(address_info, value, plc)  # 确保写入成功

    def confirm_write_success(self, address_info: dict, value: Union[int, float, bool, str], plc):
        """向 plc 写入数据, 并且一定会写成功.

        在通过 S7 协议向西门子plc写入 bool 数据的时候, 会出现写不成功的情况, 所以再向西门子plc写入 bool 时调用此函数.
        为了确保数据写入成功, 向任何plc写入数据都可调用此函数, 但是交互的时候每次会多读一次 plc.

        Args:
            address_info: 写入数据的地址位信息.
            value: 要写入的数据.
            plc: plc 实例.
        """
        while (plc_value := plc.execute_read(**address_info)) != value:
            self.logger.warning(f"当前地址 %s 的值是 %s != %s, %s", address_info.get("address"), plc_value,
                                value, address_info.get("description"))
            plc.execute_write(**address_info, value=value)

    def wait_time(self, wait_time: int):
        """等待时间.

        Args:
            wait_time: 等待时间.
        """
        while True:
            time.sleep(1)
            self.logger.info("等待 %s 秒", 1)
            wait_time -= 1
            if wait_time == 0:
                break

    async def send_data_to_socket_client(self, socket_instance: CygSocketServerAsyncio, client_ip: str, data: str) -> bool:
        """发送数据给下位机.

        Args:
            socket_instance: CygSocketServerAsyncio 实例.
            client_ip: 接收数据的设备ip地址.
            data: 要发送的数据.

        Return:
            bool: 是否发送成功.
        """
        status = True
        client_connection = socket_instance.clients.get(client_ip)
        if client_connection:
            byte_data = str(data).encode("UTF-8")
            await socket_instance.socket_send(client_connection, byte_data)
        else:
            self.logger.warning("发送失败: %s 未连接", client_ip)
            status = False
        return status

    async def operate_func_socket(self, byte_data) -> str:
        """操作并返回数据."""
        str_data = byte_data.decode("UTF-8")  # 解析接收的下位机数据
        receive_dict = json.loads(str_data)
        for receive_key, receive_info in receive_dict.items():
            self.logger.info("收到的下位机关键字是: %s", receive_key)
            self.logger.info("收到的下位机关键字对应的数据是: %s", receive_info)
            reply_data = await getattr(self, receive_key)(receive_info)
            self.logger.info("返回的数据是: %s", reply_data)
            return str(reply_data)
        return "OK"

    def wait_eap_reply(self, call_back: dict, **kwargs):
        """等待 eap 反馈.

        Args:
            call_back: 要执行的 call_back 信息.
        """
        wait_time = 0
        not_allow_dv_name = call_back.get("not_allow_dv_name")
        not_allow_dv_value = call_back.get("not_allow_dv_value")
        dv_name = call_back["dv_name"]
        while not self.get_dv_value_with_name(dv_name):
            time.sleep(1)
            wait_time += 1
            if wait_time == 5:
                self.set_dv_value_with_name(not_allow_dv_name, not_allow_dv_value)
                break
            self.logger.info("eap 未反馈 %s 请求, 已等待 %s 秒", dv_name, wait_time)

        self.set_dv_value_with_name(dv_name, False)

    def clean_eap_reply(self, call_back: dict, **kwargs):
        """清空 eap 已回馈标识.

        Args:
            call_back: 要执行的 call_back 信息.
        """
        dv_name = call_back["dv_name"]
        self.set_dv_value_with_name(dv_name, False)

    def set_time_dv_value(self, call_back: dict, **kwargs):
        """设置时间 dv 的值.

        Args:
            call_back: 要执行的 call_back 信息.
        """
        time_now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:24:]
        dv_name = call_back["dv_name"]
        self.set_dv_value_with_name(dv_name, time_now_str)
        self.config_instance.update_config_dv_value(dv_name, time_now_str)

    def set_dv_value_from_database(self, call_back: dict, **kwargs):
        """从数据库获取数据设置 dv 的值.

        Args:
            call_back: 要执行的 call_back 信息.
        """

    def _is_send_event(self, event_name: str = None):
        """判断是否要发送事件.

        Arg:
            event_name: 要发送的事件名称, 默认 None.
        """
        if event_name:
            self.send_s6f11(event_name)

    def _on_rcmd_pp_select(self, recipe_name: str, equipment_name: str):
        """eap 切换配方.

        Args:
            recipe_name: 要切换的配方名称.
            equipment_name: 设备名称.
        """
        pp_select_recipe_id = self.config_instance.get_recipe_id_with_name(recipe_name)
        self.set_sv_value_with_name("pp_select_recipe_name", recipe_name)
        self.set_sv_value_with_name("pp_select_recipe_id", pp_select_recipe_id)

        # 执行切换配方操作
        if self._open_flag:
            self.execute_call_backs(self.config["signal_address"][equipment_name]["pp_select"]["call_backs"], equipment_name)

        current_recipe_id = self.get_sv_value_with_name("current_recipe_id")
        current_recipe_name = self.config_instance.get_recipe_name_with_id(current_recipe_id)

        # 保存当前配方到本地
        self.set_sv_value_with_name("current_recipe_name", current_recipe_name)
        self.config_instance.update_config_sv_value("current_recipe_id", current_recipe_id)
        self.config_instance.update_config_sv_value("current_recipe_name", current_recipe_name)

    def _on_rcmd_new_lot(self, lot_name: str, lot_quality: int, equipment_name: str):
        """eap 开工单.

        Args:
            lot_name: 工单名称.
            lot_quality: 工单数量.
            equipment_name: 设备名称.
        """
        self.set_sv_value_with_name("current_lot_name", lot_name)
        self.set_sv_value_with_name("lot_quality", lot_quality)
        if self._open_flag:
            self.execute_call_backs(self.config["signal_address"][equipment_name]["new_lot"]["call_backs"], equipment_name)

    def _on_s07f19(self, *args):
        """查看设备的所有配方."""
        self.logger.info("收到的参数是: %s", args)
        return self.stream_function(7, 20)(self.config_instance.get_all_recipe_names())

    def _on_s02f17(self, *args) -> SecsS02F18:
        """获取设备时间.

        Returns:
            SecsS02F18: SecsS02F18 实例.
        """
        self.logger.info("收到的参数是: %s", args)
        current_time_str = datetime.now().strftime("%Y%m%d%H%M%S%C")
        return self.stream_function(2, 18)(current_time_str)

    def _on_s02f31(self, *args):
        """设置设备时间."""
        function = self.settings.streams_functions.decode(args[1])
        parser_result = function.get()
        date_time_str = parser_result
        if len(date_time_str) not in (14, 16):
            self.logger.info("时间格式错误: %s 不是14或16个数字", date_time_str)
            return self.stream_function(2, 32)(TIACK.TIME_SET_FAIL)
        current_time_str = datetime.now().strftime("%Y%m%d%H%M%S%C")
        self.logger.info("当前时间: %s", current_time_str)
        self.logger.info("设置时间: %s", date_time_str)
        status = self.set_date_time(date_time_str)
        current_time_str = datetime.now().strftime("%Y%m%d%H%M%S%C")
        if status:
            self.logger.info(f"设置成功, 当前时间: %s", current_time_str)
            ti_ack = TIACK.ACK
        else:
            self.logger.info("设置失败, 当前时间: %s", current_time_str)
            ti_ack = TIACK.TIME_SET_FAIL
        return self.stream_function(2, 32)(ti_ack)

    def _on_s10f03(self, *args):
        """Eap 下发弹框信息."""
        function = self.settings.streams_functions.decode(args[1])
        display_data = function.get()
        terminal_id = display_data.get("TID", 0)
        terminal_text = display_data.get("TEXT", "")
        self.logger.info("接收到的弹框信息是, terminal_id: %s, terminal_text: %s", terminal_id, terminal_text)
        return self.stream_function(10, 4)(1)

    @staticmethod
    def set_date_time(modify_time_str) -> bool:
        """设置windows系统日期和时间.

        Args:
            modify_time_str (str): 要修改的时间字符串.

        Returns:
            bool: 修改成功或者失败.
        """
        date_time = datetime.strptime(modify_time_str, "%Y%m%d%H%M%S%f")
        date_command = f"date {date_time.year}-{date_time.month}-{date_time.day}"
        result_date = subprocess.run(date_command, shell=True, check=False)
        time_command = f"time {date_time.hour}:{date_time.minute}:{date_time.second}"
        result_time = subprocess.run(time_command, shell=True, check=False)
        if result_date.returncode == 0 and result_time.returncode == 0:
            return True
        return False
