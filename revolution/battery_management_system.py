from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntFlag
from logging import getLogger
from struct import pack, unpack
from typing import ClassVar

from can import BusABC, Message

BATTERY_CELL_COUNT: int = 36
BATTERY_THERMISTOR_COUNT: int = 18
_logger = getLogger(__name__)


class BatteryFlag(IntFlag):
    CLEAR = 0b000000
    OVERVOLTAGE = 0b000001
    UNDERVOLTAGE = 0b000010
    OVERTEMPERATURE = 0b000100
    UNDERTEMPERATURE = 0b001000
    OVERCURRENT = 0b010000
    UNDERCURRENT = 0b100000


@dataclass
class Information(ABC):
    MESSAGE_IDENTIFIERS: ClassVar[range]
    FORMAT: ClassVar[str]
    message_identifier: int


@dataclass
class PartialInformation(Information, ABC):
    FORMAT = '<eeee'
    datum_1: float
    datum_2: float
    datum_3: float
    datum_4: float

    @abstractmethod
    def _get_keys(self) -> tuple[int, int, int, int]:
        pass

    @property
    def data(self) -> dict[int, float]:
        key_1, key_2, key_3, key_4 = self._get_keys()

        return {
            key_1: self.datum_1,
            key_2: self.datum_2,
            key_3: self.datum_3,
            key_4: self.datum_4
        }


@dataclass
class BatteryPackFlagsInformation(Information, ABC):
    FORMAT = '<Q'
    CELL_FLAG: ClassVar[BatteryFlag]
    THERMISTOR_FLAG: ClassVar[BatteryFlag]
    CURRENT_FLAG: ClassVar[BatteryFlag]
    flags: int

    @property
    def cell_flags(self) -> dict[int, BatteryFlag]:
        flags = {}

        for i in range(BATTERY_CELL_COUNT):
            if self.flags & (1 << i):
                flag = self.CELL_FLAG
            else:
                flag = BatteryFlag(0)

            flags[i] = flag

        return flags

    @property
    def thermistor_flags(self) -> dict[int, BatteryFlag]:
        flags = {}

        for i in range(BATTERY_THERMISTOR_COUNT):
            if self.flags & (1 << (i + 36)):
                flag = self.THERMISTOR_FLAG
            else:
                flag = BatteryFlag(0)

            flags[i] = flag

        return flags

    @property
    def current_flag(self) -> BatteryFlag:
        if self.flags & (1 << 54):
            flag = self.CURRENT_FLAG
        else:
            flag = BatteryFlag(0)

        return flag


# Important
@dataclass
class StatusesAndHVInformation(Information):
    MESSAGE_IDENTIFIERS = range(0, 1)
    FORMAT = '<BBeee'
    statuses: int
    flag_hold: int
    reserved: float
    HV_voltage: float
    HV_current: float

    @property
    def relay_status(self) -> bool:
        return bool(self.statuses & (1 << 0))

    @property
    def electric_safe_discharge_status(self) -> bool:
        return bool(self.statuses & (1 << 1))

    @property
    def discharge_status(self) -> bool:
        return bool(self.statuses & (1 << 2))


@dataclass
class OverBatteryFlagsInformation(
        BatteryPackFlagsInformation,
):
    MESSAGE_IDENTIFIERS = range(1, 2)
    CELL_FLAG = BatteryFlag.OVERVOLTAGE
    THERMISTOR_FLAG = BatteryFlag.OVERTEMPERATURE
    CURRENT_FLAG = BatteryFlag.OVERCURRENT


@dataclass
class UnderBatteryFlagsInformation(
    BatteryPackFlagsInformation
):
    MESSAGE_IDENTIFIERS = range(2, 3)
    CELL_FLAG = BatteryFlag.UNDERVOLTAGE
    THERMISTOR_FLAG = BatteryFlag.UNDERTEMPERATURE
    CURRENT_FLAG = BatteryFlag.UNDERCURRENT


@dataclass
class LVInformation(Information):
    MESSAGE_IDENTIFIERS = range(3, 4)
    FORMAT = '<eeee'
    LV_voltage: float
    LV_current: float
    supp_voltage: float
    rolling_min_LV_voltage: float


# Battery Flag Event
@dataclass
class OverBatteryFlagsHoldInformation(
        BatteryPackFlagsInformation,
):
    MESSAGE_IDENTIFIERS = range(4, 5)
    CELL_FLAG = BatteryFlag.OVERVOLTAGE
    THERMISTOR_FLAG = BatteryFlag.OVERTEMPERATURE
    CURRENT_FLAG = BatteryFlag.OVERCURRENT


@dataclass
class UnderBatteryFlagsHoldInformation(
    BatteryPackFlagsInformation
):
    MESSAGE_IDENTIFIERS = range(5, 6)
    CELL_FLAG = BatteryFlag.UNDERVOLTAGE
    THERMISTOR_FLAG = BatteryFlag.UNDERTEMPERATURE
    CURRENT_FLAG = BatteryFlag.UNDERCURRENT


@dataclass
class OvervoltageHoldInformation(Information):
    MESSAGE_IDENTIFIERS = range(6, 7)
    FORMAT = '<HHee'
    hold_elapsed_count: int
    hold_OV_count: int
    hold_OV_max: float
    reserved: float


@dataclass
class UndervoltageHoldInformation(Information):
    MESSAGE_IDENTIFIERS = range(7, 8)
    FORMAT = '<HHee'
    hold_elapsed_count: int
    hold_UV_count: int
    hold_UV_min: float
    reserved: float


@dataclass
class OvertemperatureHoldInformation(Information):
    MESSAGE_IDENTIFIERS = range(8, 9)
    FORMAT = '<HHee'
    hold_elapsed_count: int
    hold_OT_count: int
    hold_OT_max: float
    reserved: float


@dataclass
class UndertemperatureHoldInformation(Information):
    MESSAGE_IDENTIFIERS = range(9, 10)
    FORMAT = '<HHee'
    hold_elapsed_count: int
    hold_UT_count: int
    hold_UT_min: float
    reserved: float


@dataclass
class OvercurrentHoldInformation(Information):
    MESSAGE_IDENTIFIERS = range(10, 11)
    FORMAT = '<HHee'
    hold_elapsed_count: int
    hold_OC_count: int
    hold_OC_max: float
    reserved: float


@dataclass
class UndercurrentHoldInformation(Information):
    MESSAGE_IDENTIFIERS = range(11, 12)
    FORMAT = '<HHee'
    hold_elapsed_count: int
    hold_UC_count: int
    hold_UC_min: float
    reserved: float


# Voltages / Temperatures
@dataclass
class CellVoltagesInformation(PartialInformation):
    MESSAGE_IDENTIFIERS = range(18, 27)

    def _get_keys(self) -> tuple[int, int, int, int]:
        i = self.message_identifier - 18
        return (4 * i, 4 * i + 1, 4 * i + 2, 4 * i + 3)


@dataclass
class ThermistorTemperaturesInformation(PartialInformation):
    MESSAGE_IDENTIFIERS = range(27, 32)

    def _get_keys(self) -> tuple[int, int, int, int]:
        i = self.message_identifier - 27
        return (4 * i, 4 * i + 1, 4 * i + 2, 4 * i + 3)


@dataclass
class BatteryManagementSystem:
    BASE_ADDRESS: ClassVar[int] = 0x400
    can_bus: BusABC
    driver_controls_base_address: int

    def _send(
            self,
            message_identifier: int,
            data: bytes,
            timeout: float | None = None,
    ) -> None:
        if len(data) > 8:
            raise ValueError('data is less than 8 bytes')

        arbitration_id = self.driver_controls_base_address + message_identifier
        message = Message(
            arbitration_id=arbitration_id,
            data=data,
            is_extended_id=False,
        )

        self.can_bus.send(message, timeout)

    def open_relay(self, timeout: float | None = None) -> None:
        self._send(0x0, b'', timeout)

    def close_relay(self, timeout: float | None = None) -> None:
        self._send(0x1, b'', timeout)

    def discharge(self, timeout: float | None = None) -> None:
        self._send(0x2, b'', timeout)

    def clear(self, timeout: float | None = None) -> None:
        self._send(0x3, b'', timeout)

    def update_horn(self, status: bool, timeout: float | None = None) -> None:
        self._send(0x4, pack('<B', status), timeout)

    def heartbeat(self, timeout: float | None = None) -> None:
        self._send(0x1f, b'', timeout)

    INFORMATION_TYPES: ClassVar[tuple[type[Information], ...]] = (
        # Important
        StatusesAndHVInformation,
        OverBatteryFlagsInformation,
        UnderBatteryFlagsInformation,
        LVInformation,
        # Battery Flag Event
        OverBatteryFlagsHoldInformation,
        UnderBatteryFlagsHoldInformation,
        OvervoltageHoldInformation,
        OvertemperatureHoldInformation,
        OvercurrentHoldInformation,
        UndervoltageHoldInformation,
        UndertemperatureHoldInformation,
        UndercurrentHoldInformation,
        # Voltages / Temperatures
        CellVoltagesInformation,
        ThermistorTemperaturesInformation,
    )

    def parse(self, message: Message) -> Information | None:
        device_identifier = message.arbitration_id >> 5

        if self.BASE_ADDRESS != device_identifier << 5:
            return None

        message_identifier = message.arbitration_id & ((1 << 5) - 1)
        information = None

        for type_ in self.INFORMATION_TYPES:
            if message_identifier in type_.MESSAGE_IDENTIFIERS:
                information = type_(
                    message_identifier,
                    *unpack(type_.FORMAT, message.data),
                )

                break

        return information
