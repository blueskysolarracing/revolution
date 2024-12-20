from dataclasses import dataclass
from logging import getLogger
from typing import ClassVar

from revolution.application import Application
from revolution.environment import Endpoint
from revolution.worker import Worker

_logger = getLogger(__name__)


@dataclass
class Miscellaneous(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.MISCELLANEOUS

    def _setup(self) -> None:
        super()._setup()

        self._light_worker = Worker(target=self._light)

        self._light_worker.start()

    def _teardown(self) -> None:
        self._light_worker.join()

    def _light(self) -> None:
        while (
                not self._stoppage.wait(
                    self.environment.settings.miscellaneous_light_timeout,
                )
        ):
            with self.environment.contexts() as contexts:
                left_indicator_light_status_input = (
                    contexts.miscellaneous_left_indicator_light_status_input
                )
                right_indicator_light_status_input = (
                    contexts.miscellaneous_right_indicator_light_status_input
                )
                hazard_lights_status_input = (
                    contexts.miscellaneous_hazard_lights_status_input
                )
                daytime_running_lights_status_input = (
                    contexts.miscellaneous_daytime_running_lights_status_input
                )
                horn_status_input = contexts.miscellaneous_horn_status_input
                backup_camera_control_status_input = (
                    contexts.miscellaneous_backup_camera_control_status_input
                )
                display_backlight_status_input = (
                    contexts.miscellaneous_display_backlight_status_input
                )
                brake_lights_status_input = (
                    contexts.miscellaneous_brake_status_input
                )

            if (
                    left_indicator_light_status_input
                    or right_indicator_light_status_input
                    or hazard_lights_status_input
            ):
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_indicator_lights_pwm
                    .enable()
                )
            else:
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_indicator_lights_pwm
                    .disable()
                )

            if left_indicator_light_status_input or hazard_lights_status_input:
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_left_indicator_light_pwm
                    .enable()
                )
            else:
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_left_indicator_light_pwm
                    .disable()
                )

            if (
                    right_indicator_light_status_input
                    or hazard_lights_status_input
            ):
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_right_indicator_light_pwm
                    .enable()
                )
            else:
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_right_indicator_light_pwm
                    .disable()
                )

            if daytime_running_lights_status_input:
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_daytime_running_lights_pwm
                    .enable()
                )
            else:
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_daytime_running_lights_pwm
                    .disable()
                )

            if brake_lights_status_input:
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_brake_lights_pwm
                    .enable()
                )
            else:
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_brake_lights_pwm
                    .disable()
                )

            (
                self
                .environment
                .peripheries
                .miscellaneous_horn_switch_gpio
                .write(horn_status_input)
            )
            (
                self
                .environment
                .peripheries
                .miscellaneous_backup_camera_control_switch_gpio
                .write(backup_camera_control_status_input)
            )
            (
                self
                .environment
                .peripheries
                .miscellaneous_display_backlight_switch_gpio
                .write(display_backlight_status_input)
            )
