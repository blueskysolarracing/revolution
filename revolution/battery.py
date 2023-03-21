from multiprocessing import get_logger
from queue import Queue
from enum import Enum, auto
from dataclasses import dataclass, field

from periphery import GPIO, SPI

from revolution.drivers import LTC6810
from revolution.application import Application


_logger = get_logger()

############# CONSTANTS FOR BMS #############
BMS_MODULE_NUM_CELLS = 5
BMS_MODULE_NUM_VOLTAGES = BMS_MODULE_NUM_CELLS
BMS_MODULE_NUM_STATE_OF_CHARGES = BMS_MODULE_NUM_CELLS

BMS_MODULE_NUM_TEMPERATURE_SENSOR = 3
BMS_MODULE_NUM_TEMPERATURES = BMS_MODULE_NUM_TEMPERATURE_SENSOR


def init_queue_from_arr(input_arr: list[float]) -> Queue[float]:
    queue: Queue[float] = Queue()
    for element in input_arr:
        queue.put(element)
    return queue


def get_queue_average(queue: Queue[float]) -> float:
    total = 0.0
    for element in queue.queue:
        total += element
    return 0.0 if queue.qsize() == 0 else total / queue.qsize()


class BMSModule:
    spi: SPI
    gpio_b: GPIO

    class GetMode(Enum):
        GET_MOST_RECENT = auto()
        GET_PAST_AVERAGE = auto()
        GET_FILTERED_RESULT = auto()

    def __init__(self, battery_id: int) -> None:
        self.ltc6810 = LTC6810(spi=self.spi, gpio_b=self.gpio_b)

        self.battery_id = battery_id
        self._current = 0.0
        self._state_of_charge_arr = [0.0] * BMS_MODULE_NUM_STATE_OF_CHARGES

        self._voltage_arr = self.ltc6810.read_voltage()  # voltage of each cell
        self._past_voltage_queue = init_queue_from_arr(self._voltage_arr)
        self._temperature_arr = self.ltc6810.read_temp(0, 0, 0, 0, 0)
        self._past_temp_queue = init_queue_from_arr(self._temperature_arr)

        # TODO: initialize battery algo using EKF

    def get_temperature(self, temperatures: list[float], get_mode: GetMode) -> None:

        for i in range(BMS_MODULE_NUM_TEMPERATURES):
            if get_mode == BMSModule.GetMode.GET_MOST_RECENT:
                temperatures[i] = self._temperature_arr[i]
            elif get_mode == BMSModule.GetMode.GET_PAST_AVERAGE:
                temperatures[i] = get_queue_average(self._past_temp_queue)
            elif get_mode == BMSModule.GetMode.GET_FILTERED_RESULT:
                pass

    def get_voltage(self, voltages: list[float], get_mode: GetMode) -> None:

        for i in range(BMS_MODULE_NUM_VOLTAGES):
            if get_mode == BMSModule.GetMode.GET_MOST_RECENT:
                voltages[i] = self._voltage_arr[i]
            elif get_mode == BMSModule.GetMode.GET_PAST_AVERAGE:
                voltages[i] = get_queue_average(self._past_voltage_queue)
            elif get_mode == BMSModule.GetMode.GET_FILTERED_RESULT:
                pass

    def get_state_of_charge(self, state_of_charges: list[float]) -> None:
        for i in range(BMS_MODULE_NUM_STATE_OF_CHARGES):
            state_of_charges[i] = self._state_of_charge_arr[i]

    def measure_temperature(self) -> None:
        # Note: the following function reads voltage
        local_temp_arr = self.ltc6810.read_temp(0, 0, 0, 0, 0)
        local_temp_arr = self.ltc6810.voltage_to_temp(local_temp_arr)
        for i in range(BMS_MODULE_NUM_TEMPERATURES):
            self._temperature_arr[i] = local_temp_arr[i]
            self._past_temp_queue.put(local_temp_arr[i])

    def measure_voltage(self) -> None:
        local_voltage_arr = self.ltc6810.read_voltage()
        for i in range(BMS_MODULE_NUM_VOLTAGES):
            self._voltage_arr[i] = local_voltage_arr[i]
            self._past_voltage_queue.put(local_voltage_arr[i])

    def compute_soc(self) -> None:
        local_soc_arr = [0.0] * BMS_MODULE_NUM_STATE_OF_CHARGES

        # TODO: compute algorithm with EKF_models

        for i in range(BMS_MODULE_NUM_STATE_OF_CHARGES):
            self._state_of_charge_arr[i] = local_soc_arr[i]

    def set_current(self, current: float) -> None:
        self._current = current


@dataclass
class Battery(Application):
    bms_modules: list[BMSModule] = field(default_factory=lambda: [BMSModule(i) for i in range(5)])


