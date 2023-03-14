from dataclasses import dataclass, field
from functools import partial
from logging import getLogger
from time import sleep
from typing import ClassVar

from periphery import GPIO, PWM

from revolution.application import Application
from revolution.environment import Endpoint

_logger = getLogger(__name__)


@dataclass
class Miscellaneous(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.MISCELLANEOUS
    timeout: ClassVar[float] = 0.01
    indicator_lights_pwm: PWM \
        = field(default_factory=partial(PWM, 0, 0))  # TODO
    left_indicator_light_pwm: PWM \
        = field(default_factory=partial(PWM, 0, 0))  # TODO
    right_indicator_light_pwm: PWM \
        = field(default_factory=partial(PWM, 0, 0))  # TODO
    daytime_running_lights_pwm: PWM \
        = field(default_factory=partial(PWM, 0, 0))  # TODO
    brake_lights_pwm: PWM = field(default_factory=partial(PWM, 0, 0))  # TODO
    horn_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    fan_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO

    def __post_init__(self) -> None:
        self.indicator_lights_pwm.period = 0.8
        self.indicator_lights_pwm.duty_cycle = 0.5
        self.left_indicator_light_pwm.period = 0.001
        self.left_indicator_light_pwm.duty_cycle = 0.25
        self.right_indicator_light_pwm.period = 0.001
        self.right_indicator_light_pwm.duty_cycle = 0.25
        self.daytime_running_lights_pwm.period = 0.001
        self.daytime_running_lights_pwm.duty_cycle = 0.25
        self.brake_lights_pwm.period = 0.001
        self.brake_lights_pwm.duty_cycle = 0.25

    def _setup(self) -> None:
        super()._setup()

        self._worker_pool.add(self.__update)

    def __update(self) -> None:
        while self._status:
            with self.environment.read() as data:
                left_indicator_light_status_input \
                    = data.left_indicator_light_status_input
                right_indicator_light_status_input \
                    = data.right_indicator_light_status_input
                hazard_lights_status_input = data.hazard_lights_status_input
                daytime_running_lights_status_input \
                    = data.daytime_running_lights_status_input
                brake_lights_status_input = data.brake_status_input
                horn_status_input = data.horn_status_input
                fan_status_input = data.fan_status_input

            if left_indicator_light_status_input \
                    or right_indicator_light_status_input \
                    or hazard_lights_status_input:
                self.indicator_lights_pwm.enable()
            else:
                self.indicator_lights_pwm.disable()

            if left_indicator_light_status_input or hazard_lights_status_input:
                self.left_indicator_light_pwm.enable()
            else:
                self.left_indicator_light_pwm.disable()

            if right_indicator_light_status_input \
                    or hazard_lights_status_input:
                self.right_indicator_light_pwm.enable()
            else:
                self.right_indicator_light_pwm.disable()

            if daytime_running_lights_status_input:
                self.daytime_running_lights_pwm.enable()
            else:
                self.daytime_running_lights_pwm.disable()

            if brake_lights_status_input:
                self.brake_lights_pwm.enable()
            else:
                self.brake_lights_pwm.disable()

            if horn_status_input:
                self.horn_switch_gpio.write(True)
            else:
                self.horn_switch_gpio.write(False)

            if fan_status_input:
                self.fan_switch_gpio.write(True)
            else:
                self.fan_switch_gpio.write(False)

            sleep(self.timeout)
