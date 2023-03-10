from dataclasses import dataclass, field
from functools import partial
from logging import getLogger
from periphery import GPIO, SPI
from threading import Event
from time import sleep
from typing import ClassVar

from revolution.application import Application
from revolution.drivers import M2096
from revolution.environment import Endpoint

_logger = getLogger(__name__)


@dataclass
class Motor(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.MOTOR
    timeout: ClassVar[float] = 0.01
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
    variable_field_magnet_up_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    variable_field_magnet_down_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    revolution_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in', 'both'))  # TODO
    controller: M2096 = field(init=False)
    __usage: Event = field(default_factory=Event, init=False)

    def __post_init__(self) -> None:
        self.controller = M2096(
            self.acceleration_potentiometer_spi,
            self.regeneration_potentiometer_spi,
            self.main_switch_gpio,
            self.forward_or_reverse_switch_gpio,
            self.power_or_economical_switch_gpio,
            self.variable_field_magnet_up_switch_gpio,
            self.variable_field_magnet_down_switch_gpio,
            self.revolution_gpio,
        )

    @property
    def _controller_status(self) -> bool:
        return self.__usage.is_set()

    def _setup(self) -> None:
        super()._setup()

        self._worker_pool.add(self.__update_usage)
        self._worker_pool.add(self.__update_spi)
        self._worker_pool.add(self.__update_gpio)
        self._worker_pool.add(self.__update_variable_field_magnet)
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
                    acceleration_input = max(
                        data.acceleration_pedal_input,
                        data.acceleration_paddle_input,
                    )
                    regeneration_input = max(
                        data.regeneration_pedal_input,
                        data.regeneration_paddle_input,
                    )
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
                direction_input = data.direction_input
                economical_mode_input = data.economical_mode_input

            self.controller.direct(direction_input)
            self.controller.economize(economical_mode_input)
            sleep(self.timeout)

    def __update_variable_field_magnet(self) -> None:
        while self._status:
            with self.environment.read_and_write() as data:
                min_value = min(
                    data.variable_field_magnet_up_input,
                    data.variable_field_magnet_down_input,
                )
                data.variable_field_magnet_up_input -= min_value
                data.variable_field_magnet_down_input -= min_value

                if data.variable_field_magnet_up_input:
                    variable_field_magnet_input = 1
                    data.variable_field_magnet_up_input -= 1
                elif data.variable_field_magnet_down_input:
                    variable_field_magnet_input = -1
                    data.variable_field_magnet_down_input -= 1
                else:
                    variable_field_magnet_input = 0

            if variable_field_magnet_input > 0:
                self.controller.variable_field_magnet_up()
            elif variable_field_magnet_input < 0:
                self.controller.variable_field_magnet_down()

            sleep(self.timeout)

    def __update_revolution(self) -> None:
        while self._status:
            revolution_period = self.controller.revolution_period

            with self.environment.write() as data:
                data.revolution_period = revolution_period

            sleep(self.timeout)
