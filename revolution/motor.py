from dataclasses import dataclass, field
from functools import partial
from logging import getLogger
from math import inf
from periphery import GPIO, SPI
from threading import Lock
from time import sleep, time
from typing import ClassVar

from revolution.application import Application
from revolution.environment import Direction, Endpoint

_logger = getLogger(__name__)


@dataclass
class MotorController:
    @staticmethod
    def __position_potentiometer(
            spi: SPI,
            position: int,
            eeprom: bool,
    ) -> None:
        if not 0 <= position <= 256:
            raise ValueError('position not between 0 and 256')

        raw_data = position

        if eeprom:
            raw_data |= 1 << 13

        data = [raw_data >> 8, raw_data & ((1 << 8) - 1)]

        spi.transfer(data)

    main_switch_timeout: ClassVar[float] = 5
    vfm_switch_timeout: ClassVar[float] = 0.2
    revolution_timeout: ClassVar[float] = 10
    acceleration_potentiometer_spi: SPI \
        = field(default_factory=partial(SPI, '', 0, 1))  # TODO
    regeneration_potentiometer_spi: SPI \
        = field(default_factory=partial(SPI, '', 0, 1))  # TODO
    main_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    forward_or_reverse_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    power_or_economical_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    vfm_up_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    vfm_down_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    revolution_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in', 'rising'))  # TODO

    def __post_init__(self) -> None:
        self.accelerate(0, True)
        self.regenerate(0, True)

    @property
    def revolution_period(self) -> float:
        if not self.revolution_gpio.poll(self.revolution_timeout):
            return inf

        timestamp = time()

        if not self.revolution_gpio.poll(self.revolution_timeout):
            return inf

        return time() - timestamp

    @property
    def status(self) -> bool:
        return not self.main_switch_gpio.read()

    def accelerate(self, acceleration: float, eeprom: bool = False) -> None:
        if not 0 <= acceleration <= 1:
            raise ValueError('acceleration not between 0 and 1')

        position = round(256 * acceleration)

        self.__position_potentiometer(
            self.acceleration_potentiometer_spi,
            position,
            eeprom,
        )

    def regenerate(self, regeneration: float, eeprom: bool = False) -> None:
        if not 0 <= regeneration <= 1:
            raise ValueError('regeneration not between 0 and 1')

        position = round(256 * regeneration)

        self.__position_potentiometer(
            self.regeneration_potentiometer_spi,
            position,
            eeprom,
        )

    def state(self, status: bool) -> None:
        wait = status and not self.status

        self.main_switch_gpio.write(not status)

        if wait:
            sleep(self.main_switch_timeout)

    def direct(self, direction: Direction) -> None:
        match direction:
            case Direction.FORWARD:
                raw_direction = False
            case Direction.BACKWARD:
                raw_direction = True
            case _:
                raise ValueError(f'unknown direction {direction}')

        self.forward_or_reverse_switch_gpio.write(raw_direction)

    def economize(self, mode: bool) -> None:
        self.power_or_economical_switch_gpio.write(mode)

    def gear_up(self) -> None:
        self.vfm_up_switch_gpio.write(True)
        sleep(self.vfm_switch_timeout)
        self.vfm_up_switch_gpio.write(False)

    def gear_down(self) -> None:
        self.vfm_down_switch_gpio.write(True)
        sleep(self.vfm_switch_timeout)
        self.vfm_down_switch_gpio.write(False)


@dataclass
class Motor(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.MOTOR
    controller: MotorController = field(default_factory=MotorController)
    controller_status: bool = field(init=False)
    controller_status_lock: Lock = field(default_factory=Lock, init=False)

    def __post_init__(self) -> None:
        with self.controller_status_lock:
            self.controller_status = self.controller.status

    def _setup(self) -> None:
        super()._setup()

        self._worker_pool.add(self.__update_status)
        self._worker_pool.add(self.__update_spi)
        self._worker_pool.add(self.__update_gpio)
        self._worker_pool.add(self.__update_gear)
        self._worker_pool.add(self.__update_revolution)

    def __update_status(self) -> None:
        while self._status:
            with self._environment.read() as data:
                status_input = data.motor_status_input

            if self.controller.status != status_input:
                self.controller.state(status_input)

                with self.controller_status_lock:
                    self.controller_status = status_input

    def __update_spi(self) -> None:
        while self._status:
            with self.controller_status_lock:
                controller_status = self.controller_status

            if controller_status:
                with self._environment.read() as data:
                    acceleration_input = data.motor_acceleration_input
                    regeneration_input = data.motor_regeneration_input

                self.controller.accelerate(acceleration_input)
                self.controller.regenerate(regeneration_input)
            else:
                self.controller.accelerate(0)
                self.controller.regenerate(0)

    def __update_gpio(self) -> None:
        while self._status:
            with self._environment.read() as data:
                directional_input = data.motor_directional_input
                economical_mode_input = data.motor_economical_mode_input

            self.controller.direct(directional_input)
            self.controller.economize(economical_mode_input)

    def __update_gear(self) -> None:
        while self._status:
            with self._environment.read_and_write() as data:
                if data.motor_gear_input > 0:
                    gear_index_input = 1
                elif data.motor_gear_input < 0:
                    gear_index_input = -1
                else:
                    gear_index_input = 0

                data.motor_gear_input -= gear_index_input

            if gear_index_input > 0:
                self.controller.gear_up()
            elif gear_index_input < 0:
                self.controller.gear_down()

    def __update_revolution(self) -> None:
        while self._status:
            revolution_period = self.controller.revolution_period

            with self._environment.write() as data:
                data.motor_revolution_period = revolution_period
