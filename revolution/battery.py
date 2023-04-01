from multiprocessing import get_logger
from collections import deque
from enum import Enum, auto
from dataclasses import dataclass, field
from functools import partial
from typing import ClassVar

from periphery import GPIO, SPI

from revolution.drivers import LTC6810
from revolution.application import Application

_logger = get_logger()

MAX_DEQUE_LEN = 5


def get_queue_avg(queue: deque[float]) -> float:
    return sum(list(queue)) / len(list(queue)) if len(list(queue)) > 0 else 0.0


@dataclass
class BMSModule:
    spi: SPI
    gpio_b: GPIO
    bms_module_id: int

    NUM_CELLS: ClassVar[int] = LTC6810.NUM_VOLTAGES
    NUM_VOLTAGES: ClassVar[int] = NUM_CELLS
    NUM_STATE_OF_CHARGES: ClassVar[int] = NUM_CELLS

    NUM_TEMPERATURE_SENSOR: ClassVar[int] = LTC6810.NUM_TEMP_SENSORS
    NUM_TEMPERATURES: ClassVar[int] = NUM_TEMPERATURE_SENSOR

    ltc6810: LTC6810 = field(init=False)
    voltage_arr: list[float] = field(init=False)
    temperature_arr: list[float] = field(init=False)
    past_voltage_arr: list[deque[float]] = field(default_factory=list)
    past_temp_arr: list[deque[float]] = field(default_factory=list)
    state_of_charge_arr: list[float] = field(default_factory=lambda: [0.0] * BMSModule.NUM_STATE_OF_CHARGES)
    current: float = 0.0

    class GetMode(Enum):
        GET_MOST_RECENT = auto()
        GET_PAST_AVERAGE = auto()
        GET_FILTERED_RESULT = auto()

    def __post_init__(self) -> None:
        self.ltc6810 = LTC6810(self.spi, self.gpio_b)
        self.voltage_arr = self.ltc6810.read_voltage()  # voltage of each cell
        self.temperature_arr = self.ltc6810.read_temp(0, 0, 0, 0, 0)

        for i in range(self.NUM_VOLTAGES):
            self.past_voltage_arr.append(deque(maxlen=MAX_DEQUE_LEN))
            self.past_voltage_arr[i].append((self.voltage_arr[i]))

            self.past_temp_arr.append(deque(maxlen=MAX_DEQUE_LEN))
            self.past_temp_arr[i].append((self.temperature_arr[i]))

        # TODO: initialize battery algo using EKF

    def get_temperature(self, temperatures: list[float], get_mode: GetMode) -> None:

        for i in range(self.NUM_TEMPERATURES):
            if get_mode == BMSModule.GetMode.GET_MOST_RECENT:
                temperatures[i] = self.temperature_arr[i]
            elif get_mode == BMSModule.GetMode.GET_PAST_AVERAGE:
                temperatures[i] = get_queue_avg(self.past_temp_arr[i])
            elif get_mode == BMSModule.GetMode.GET_FILTERED_RESULT:
                pass

    def get_voltage(self, voltages: list[float], get_mode: GetMode) -> None:

        for i in range(self.NUM_VOLTAGES):
            if get_mode == BMSModule.GetMode.GET_MOST_RECENT:
                voltages[i] = self.voltage_arr[i]
            elif get_mode == BMSModule.GetMode.GET_PAST_AVERAGE:
                voltages[i] = get_queue_avg(self.past_voltage_arr[i])
            elif get_mode == BMSModule.GetMode.GET_FILTERED_RESULT:
                pass

    def get_state_of_charge(self, state_of_charges: list[float]) -> None:
        for i in range(self.NUM_STATE_OF_CHARGES):
            state_of_charges[i] = self.state_of_charge_arr[i]

    def measure_temperature(self) -> None:
        # Note: the following function reads voltage
        local_volt_arr = self.ltc6810.read_temp(0, 0, 0, 0, 0)
        local_temp_arr = self.ltc6810.voltage_to_temp(local_volt_arr)
        for i in range(self.NUM_TEMPERATURES):
            self.temperature_arr[i] = local_temp_arr[i]
            self.past_temp_arr[i].append((local_temp_arr[i]))

    def measure_voltage(self) -> None:
        local_voltage_arr = self.ltc6810.read_voltage()
        for i in range(self.NUM_VOLTAGES):
            self.voltage_arr[i] = local_voltage_arr[i]
            self.past_voltage_arr[i].append((local_voltage_arr[i]))

    def compute_soc(self) -> None:
        local_soc_arr = [0.0] * self.NUM_STATE_OF_CHARGES

        # TODO: compute algorithm with EKF_models

        for i in range(self.NUM_STATE_OF_CHARGES):
            self.state_of_charge_arr[i] = local_soc_arr[i]

    def set_current(self, current: float) -> None:
        self.current = current


@dataclass
class Battery(Application):
    bms_modules: list[BMSModule] = field(init=False)
    battery_spi: SPI = field(default_factory=partial(SPI, '', 3, 1e6))    # TODO
    gpio_b: GPIO = field(default_factory=partial(GPIO, 0, 0))    # TODO
    NUM_BMS_MODULES: ClassVar[int] = 5

    def __post_init__(self):
        self.bms_modules = [BMSModule(spi=self.battery_spi, gpio_b=self.gpio_b, bms_module_id=i) for i in range(self.NUM_BMS_MODULES)]
