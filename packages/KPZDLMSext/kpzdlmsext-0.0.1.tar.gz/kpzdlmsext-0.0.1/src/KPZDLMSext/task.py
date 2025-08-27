from copy import copy
import asyncio
from dataclasses import dataclass, field
import sqlite3
from StructResult import result
from DLMS_SPODES.types import cdt, cst
from DLMS_SPODES.cosem_interface_classes.parameter import Parameter
from DLMS_SPODES.cosem_interface_classes.implementations.data import AFEOffsets, AFERegisters, AFERegister
from DLMS_SPODES.pardata import ParValues
from DLMS_SPODES_client.client import Client
from DLMS_SPODES_client import task
from DLMS_SPODES import exceptions as exc
from DLMS_SPODES.pardata import ParData
from SPODESext.parameters import DEVICE_TYPE
from semver import Version as SemVer
from .enums import Command, Status
from .parameters import CALIBRATE, AFE_OFFSETS


@dataclass
class RTCOffsetSet(task.OK):
    db_name: str
    msg: str = "Установка смещения кварца"
    phases: str = field(init=False)

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        self.phases = str(c.objects.get_n_phases())
        match str(c.objects.firmwares_description.value).split('_', maxsplit=5):
            case _, _, phases_amount, cpu_type, *_:
                if phases_amount[0] in ('1', '3'):
                    self.phases = phases_amount[0]
                else:
                    return result.Error(ValueError(F'Wrong {phases_amount=}'))
            case _:
                raise ValueError(F'Wrong device description: {c.objects.firmwares_description.value}')
        if (dev_type := c.objects.par2data(DEVICE_TYPE.VALUE)) is None:
            if isinstance((res_ := await task.Par2Data(DEVICE_TYPE.VALUE).exchange(c)), result.Error):
                return res_
            dev_type = res_.value
        match dev_type.to_str().split('_', maxsplit=1):
            case 'M2M', dev_type:
                match tuple(dev_type):
                    case self.phases, :
                        execution_type = 'P'
                    case self.phases, 'S' | "T" as execution_type:
                        pass
                    case self.phases, *wrong_execution_type:
                        return result.Error(ValueError(F'Phase amount OK. But {wrong_execution_type=}'))
                    case phase_amount_error, :
                        return result.Error(ValueError(F'{phase_amount_error=} from device type is different in description object'))
                    case _:
                        return result.Error(ValueError(F'Wrong {dev_type=}'))
            case _:
                return result.Error(ValueError(F'Wrong object value device type {DEVICE_TYPE.VALUE}'))
        # set rtc offset
        # db connect
        with sqlite3.connect(self.db_name, timeout=5) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            res = cursor.execute(
                'SELECT rtc_offset FROM RtcOffset WHERE phases_amount = ? AND execution_type = ? AND cpu = ?',
                (int(self.phases), execution_type, cpu_type))
            match res.fetchone():
                case sqlite3.Row() as row:
                    rtc_offset: int = row['rtc_offset']
                case None:
                    return result.Error(ValueError('Для данной конфигурации не найдено смещение часового кварца'))
                case _ as value:
                    return result.Error(ValueError(F'Wrong {value}'))
        return await task.WriteParValue(
            ParValues(
                par=Parameter.parse("128.0.9.0.0.255:2"),
                data=str(rtc_offset))
        ).exchange(c)


@dataclass
class Calibrate(task.Simple[list[Parameter]]):
    commands: tuple[Command, ...] = (Command.CALIBRATE_ALL,)
    timeout: int = 10
    msg: str = "Калибровка"

    async def exchange(self, c: Client) -> result.Simple[list[Parameter]] | result.Error:
        match c.objects.get_n_phases():
            case 1:
                registers = [
                    Parameter.parse("1.0.9.7.0.255:2"),
                    Parameter.parse("1.0.1.7.0.255:2"),
                    Parameter.parse("1.0.3.7.0.255:2"),
                    Parameter.parse("1.0.12.7.0.255:2"),
                    Parameter.parse("1.0.11.7.0.255:2")
                ]
            case 3:
                registers = [
                    Parameter.parse("1.0.29.7.0.255:2"),
                    Parameter.parse("1.0.21.7.0.255:2"),
                    Parameter.parse("1.0.23.7.0.255:2"),
                    Parameter.parse("1.0.32.7.0.255:2"),
                    Parameter.parse("1.0.31.7.0.255:2"),
                    Parameter.parse("1.0.49.7.0.255:2"),
                    Parameter.parse("1.0.41.7.0.255:2"),
                    Parameter.parse("1.0.43.7.0.255:2"),
                    Parameter.parse("1.0.52.7.0.255:2"),
                    Parameter.parse("1.0.51.7.0.255:2"),
                    Parameter.parse("1.0.69.7.0.255:2"),
                    Parameter.parse("1.0.61.7.0.255:2"),
                    Parameter.parse("1.0.63.7.0.255:2"),
                    Parameter.parse("1.0.72.7.0.255:2"),
                    Parameter.parse("1.0.71.7.0.255:2")
                ]
            case _:
                return result.Error(ValueError("get_n_phases wrong"))
        if isinstance((res := await task.GetFirmwareVersion().exchange(c)), result.Error):
            return res
        if cdt.encoding2semver(res.value.encoding) < SemVer(1, 3, 19):
            self.commands = (Command.CALIBRATE_A, Command.CALIBRATE_B, Command.CALIBRATE_C)
        if isinstance((res := await task.WriteParValue(ParValues(CALIBRATE.VALUE, str(Command.SET_FACTORY))).exchange(c)), result.Error):
            return res
        for command in self.commands:
            if isinstance((res := await ExecuteCalibrateCommand(command, self.timeout).exchange(c)), result.Error):
                return res
        for register in registers:
            await task.Par2Data(register).exchange(c)
            if not c.objects.par2su(register):
                await task.Par2Data(register.set_i(3)).exchange(c)
        return result.Simple(value=registers)


@dataclass
class ExecuteCalibrateCommand(task.Simple[int]):
    command: Command
    timeout: int = 20
    msg: str = "Исполнение команды калибровки"

    async def exchange(self, c: Client) -> result.Simple[int] | result.Error:
        if isinstance((res1 := await task.WriteParValue(ParValues(CALIBRATE.VALUE, str(self.command))).exchange(c)), result.Error):
            return res1
        for _ in range(self.timeout):
            await asyncio.sleep(1)
            # return result.Simple(int(Status.COMPLETE))  # for debug
            if isinstance((res2 := (await task.Par2Data(CALIBRATE.VALUE).exchange(c))), result.Error):
                return res2
            match int(res2.value):  # todo: make with DLMS typing
                case Status.COMPLETE as ret:
                    return result.Simple(value=int(ret))
                case Status.BUSY:
                    """wait"""
                case err:
                    return result.Simple(value=int(err)).append_err(exc.ITEApplication("ошибка калибровки"))
        else:
            return result.Error(exc.ITEApplication('Неполучен статус ГОТОВО'))


@dataclass
class AFEOffsetsSet(task.OK):
    db_name: str
    msg: str = "Установка смещений AFE"

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        if isinstance((res := await task.Par2Data(AFE_OFFSETS.VALUE).exchange(c)), result.Error):
            return res
        if not isinstance(res.value, AFEOffsets):
            return result.Error(ValueError(f"got value type {res.value}, expected {AFEOffsets}"))
        with (sqlite3.connect(self.db_name, timeout=5) as conn):
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            values = {name: (value, n) for name, value, n in cursor.execute(
                "SELECT o.name, AVG(o.value) AS average_value, COUNT(*) AS record_count "
                "FROM AFEOffsets o "
                "JOIN AFEs a ON o.LDN = a.LDN "
                "WHERE a.identifier = ? "
                "GROUP BY o.name "
                "ORDER BY o.name;",
                (str(res.value.identifier),)
            ).fetchall()}
            new_offsets: AFEOffsets = copy(res.value)
            for register in new_offsets.register_list:
                if (val := values.get(name := str(register.name))) is None:
                    return result.Error(ValueError(f"{register.name} is absent in db"))
                value, n = val
                # if n < 10:
                #     return result.Error(ValueError(f"the sample: <{name}>={n} is small"))
                new_reg: AFERegister = copy(register)
                if not isinstance(new_reg.value, (cdt.Digital, cdt.Float)):
                    return result.Error(ValueError(f"{register.name} has wrong type: {register.value}"))
                register.value.set(value)
        await task.WriteParDatas([ParData(AFE_OFFSETS.VALUE, new_offsets)]).exchange(c)
        return result.OK
