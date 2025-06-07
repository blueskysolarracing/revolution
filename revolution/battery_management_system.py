from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import auto, IntFlag
from logging import getLogger
from struct import unpack
from typing import ClassVar

from can import BusABC, Message

BATTERY_CELL_COUNT: int = 36
BATTERY_THERMISTOR_COUNT: int = 18
_logger = getLogger(__name__)


class BatteryFlag(IntFlag):
    OVERVOLTAGE = auto()
    UNDERVOLTAGE = auto()
    OVERTEMPERATURE = auto()
    UNDERTEMPERATURE = auto()
    OVERCURRENT = auto()


@dataclass
class Information(ABC):
    MESSAGE_IDENTIFIERS: ClassVar[range]
    FORMAT: ClassVar[str]
    message_identifier: int


@dataclass
class PartialInformation(Information, ABC):
    FORMAT = '<ff'
    datum_1: float
    datum_2: float

    @abstractmethod
    def _get_keys(self) -> tuple[int, int]:
        pass

    @property
    def data(self) -> dict[int, float]:
        key_1, key_2 = self._get_keys()

        return {key_1: self.datum_1, key_2: self.datum_2}


@dataclass
class CellVoltagesInformation(PartialInformation):
    MESSAGE_IDENTIFIERS = range(18)

    def _get_keys(self, index: int) -> tuple[int, int]:
        return 2 * self.message_identifier, 2 * self.message_identifier + 1


@dataclass
class ThermistorTemperaturesInformation(PartialInformation):
    MESSAGE_IDENTIFIERS = range(18, 27)

    def _get_keys(self, index: int) -> tuple[int, int]:
        i = self.message_identifier - 18

        return 2 * i, 2 * i + 1


@dataclass
class BusVoltageAndCurrentInformation(Information):
    MESSAGE_IDENTIFIERS = range(27, 28)
    FORMAT = '<ff'
    bus_voltage: float
    current: float


@dataclass
class StatusesInformation(Information):
    MESSAGE_IDENTIFIERS = range(28, 29)
    FORMAT = '<Q'
    statuses: int

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


@dataclass
class OvervoltageTemperatureAndCurrentFlagsInformation(
        BatteryPackFlagsInformation,
):
    MESSAGE_IDENTIFIERS = range(29, 30)
    CELL_FLAG = BatteryFlag.OVERVOLTAGE
    THERMISTOR_FLAG = BatteryFlag.OVERTEMPERATURE
    CURRENT_FLAG = BatteryFlag.OVERCURRENT


@dataclass
class UndervoltageAndTemperatureFlagsInformation(BatteryPackFlagsInformation):
    MESSAGE_IDENTIFIERS = range(30, 31)
    CELL_FLAG = BatteryFlag.UNDERVOLTAGE
    THERMISTOR_FLAG = BatteryFlag.UNDERTEMPERATURE
    CURRENT_FLAG = BatteryFlag(0)


@dataclass
class BatteryManagementSystem:
    BASE_ADDRESS: ClassVar[int] = 0x600
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

    def unflag(self, timeout: float | None = None) -> None:
        self._send(0x3, b'', timeout)

    INFORMATION_TYPES: ClassVar[tuple[type[Information], ...]] = (
        CellVoltagesInformation,
        ThermistorTemperaturesInformation,
        BusVoltageAndCurrentInformation,
        StatusesInformation,
        OvervoltageTemperatureAndCurrentFlagsInformation,
        UndervoltageAndTemperatureFlagsInformation,
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
