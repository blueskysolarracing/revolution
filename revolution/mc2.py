from dataclasses import dataclass
from math import inf
from time import sleep, time
from typing import ClassVar

from iclib.mcp4161 import MCP4161
from periphery import GPIO

from revolution.utilities import Direction


@dataclass
class MC2:
    main_switch_timeout: ClassVar[float] = 5
    variable_field_magnet_switch_timeout: ClassVar[float] = 0.2
    revolution_timeout: ClassVar[float] = 5
    MAIN_GPIO_INVERTED: ClassVar[bool] = True
    GPIO_INVERTED: ClassVar[bool] = False
    acceleration_potentiometer: MCP4161
    regeneration_potentiometer: MCP4161
    main_switch_gpio: GPIO
    forward_or_reverse_switch_gpio: GPIO
    power_or_economical_switch_gpio: GPIO
    variable_field_magnet_up_switch_gpio: GPIO
    variable_field_magnet_down_switch_gpio: GPIO
    revolution_gpio: GPIO

    def __post_init__(self) -> None:
        if (
                self.main_switch_gpio.inverted != self.MAIN_GPIO_INVERTED
                and (
                    self.forward_or_reverse_switch_gpio.inverted
                    != self.GPIO_INVERTED
                )
                and (
                    self.power_or_economical_switch_gpio.inverted
                    != self.GPIO_INVERTED
                )
                and (
                    self.variable_field_magnet_up_switch_gpio.inverted
                    != self.GPIO_INVERTED
                )
                and (
                    self.variable_field_magnet_down_switch_gpio.inverted
                    != self.GPIO_INVERTED
                )
                and self.revolution_gpio.inverted != self.GPIO_INVERTED
        ):
            raise ValueError('all GPIOs must not be inverted except main SW')

        if self.revolution_gpio.edge != 'both':
            raise ValueError('revolution gpio must trigger on both edges')

        self.accelerate(0)
        self.accelerate(0, True)
        self.regenerate(0)
        self.regenerate(0, True)
        self.main_switch_gpio.write(False)
        self.forward_or_reverse_switch_gpio.write(False)
        self.power_or_economical_switch_gpio.write(False)
        self.variable_field_magnet_up_switch_gpio.write(False)
        self.variable_field_magnet_down_switch_gpio.write(False)

    @property
    def revolution_period(self) -> float:
        if not self.revolution_gpio.poll(self.revolution_timeout):
            return inf

        timestamp = time()

        if not self.revolution_gpio.poll(self.revolution_timeout):
            return inf

        return 24 * (time() - timestamp)

    @property
    def status(self) -> bool:
        return self.main_switch_gpio.read()

    def accelerate(self, acceleration: float, eeprom: bool = False) -> None:
        if not 0 <= acceleration <= 1:
            raise ValueError('acceleration not from 0 to 1')

        step = round(acceleration * 256)

        if eeprom:
            self.acceleration_potentiometer.set_non_volatile_wiper_step(step)
        else:
            self.acceleration_potentiometer.set_volatile_wiper_step(step)

    def regenerate(self, regeneration: float, eeprom: bool = False) -> None:
        if not 0 <= regeneration <= 1:
            raise ValueError('regeneration not from 0 to 1')

        step = round(regeneration * 256)

        if eeprom:
            self.regeneration_potentiometer.set_non_volatile_wiper_step(step)
        else:
            self.regeneration_potentiometer.set_volatile_wiper_step(step)

    def state(self, status: bool) -> None:
        wait = status and not self.status

        self.main_switch_gpio.write(status)

        if wait:
            sleep(self.main_switch_timeout)

    def direct(self, direction: Direction) -> None:
        self.forward_or_reverse_switch_gpio.write(bool(direction))

    def economize(self, mode: bool) -> None:
        self.power_or_economical_switch_gpio.write(mode)

    def variable_field_magnet_up(self) -> None:
        self.variable_field_magnet_up_switch_gpio.write(True)
        sleep(self.variable_field_magnet_switch_timeout)
        self.variable_field_magnet_up_switch_gpio.write(False)

    def variable_field_magnet_down(self) -> None:
        self.variable_field_magnet_down_switch_gpio.write(True)
        sleep(self.variable_field_magnet_switch_timeout)
        self.variable_field_magnet_down_switch_gpio.write(False)
