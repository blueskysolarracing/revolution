from dataclasses import dataclass, field
from functools import partial
from logging import getLogger
from math import inf
from periphery import GPIO, SPI
from threading import Event
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
            position: float,
            eeprom: bool,
    ) -> None:
        if not 0 <= position <= 1:
            raise ValueError('position not between 0 and 1')

        raw_data = round(256 * position)

        if eeprom:
            raw_data |= 1 << 13

        data = [raw_data >> 8, raw_data & ((1 << 8) - 1)]

        spi.transfer(data)

    main_switch_timeout: ClassVar[float] = 5
    vfm_switch_timeout: ClassVar[float] = 0.2
    revolution_timeout: ClassVar[float] = 5
    acceleration_potentiometer_spi: SPI \
        = field(default_factory=partial(SPI, '', 0, 1))  # TODO
    regeneration_potentiometer_spi: SPI \
        = field(default_factory=partial(SPI, '', 0, 1))  # TODO
    main_switch_gpio: GPIO = field(
        default_factory=partial(GPIO, '', 0, 'out', inverted=True),  # TODO
    )
    forward_or_reverse_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    power_or_economical_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    vfm_up_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    vfm_down_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    revolution_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in', 'both'))  # TODO

    def __post_init__(self) -> None:
        self.accelerate(0, True)
        self.regenerate(0, True)
        self.main_switch_gpio.write(False)
        self.forward_or_reverse_switch_gpio.write(False)
        self.power_or_economical_switch_gpio.write(False)
        self.vfm_up_switch_gpio.write(False)
        self.vfm_down_switch_gpio.write(False)

    @property
    def revolution_period(self) -> float:
        if not self.revolution_gpio.poll(self.revolution_timeout):
            return inf

        timestamp = time()

        if not self.revolution_gpio.poll(self.revolution_timeout):
            return inf

        return 2 * (time() - timestamp)

    @property
    def status(self) -> bool:
        return self.main_switch_gpio.read()

    def accelerate(self, acceleration: float, eeprom: bool = False) -> None:
        self.__position_potentiometer(
            self.acceleration_potentiometer_spi,
            acceleration,
            eeprom,
        )

    def regenerate(self, regeneration: float, eeprom: bool = False) -> None:
        self.__position_potentiometer(
            self.regeneration_potentiometer_spi,
            regeneration,
            eeprom,
        )

    def state(self, status: bool) -> None:
        wait = status and not self.status

        self.main_switch_gpio.write(status)

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
    timeout: ClassVar[float] = 0.01
    controller: MotorController = field(default_factory=MotorController)
    __usage: Event = field(default_factory=Event, init=False)

    @property
    def _controller_status(self) -> bool:
        return self.__usage.is_set()

    def _setup(self) -> None:
        super()._setup()

        self._worker_pool.add(self.__update_usage)
        self._worker_pool.add(self.__update_spi)
        self._worker_pool.add(self.__update_gpio)
        self._worker_pool.add(self.__update_gear)
        self._worker_pool.add(self.__update_revolution)

    def __update_usage(self) -> None:
        while self._status:
            with self.environment.read() as data:
                status_input = data.motor_status_input

            if not status_input:
                self.__usage.clear()

            self.controller.state(status_input)

            if status_input:
                self.__usage.set()

            sleep(self.timeout)

    def __update_spi(self) -> None:
        while self._status:
            if self._controller_status:
                with self.environment.read() as data:
                    acceleration_input = data.motor_acceleration_input
                    regeneration_input = data.motor_regeneration_input
                    brake_status_input = data.brake_status_input

                if not brake_status_input and not regeneration_input:
                    self.controller.accelerate(acceleration_input)
                else:
                    self.controller.accelerate(0)

                if not brake_status_input:
                    self.controller.regenerate(regeneration_input)
                else:
                    self.controller.regenerate(0)

            sleep(self.timeout)

    def __update_gpio(self) -> None:
        while self._status:
            with self.environment.read() as data:
                direction_input = data.motor_direction_input
                economical_mode_input = data.motor_economical_mode_input

            self.controller.direct(direction_input)
            self.controller.economize(economical_mode_input)
            sleep(self.timeout)

    def __update_gear(self) -> None:
        while self._status:
            with self.environment.read_and_write() as data:
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

            sleep(self.timeout)

    def __update_revolution(self) -> None:
        while self._status:
            revolution_period = self.controller.revolution_period

            with self.environment.write() as data:
                data.motor_revolution_period = revolution_period

            sleep(self.timeout)
