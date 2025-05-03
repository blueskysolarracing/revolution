from dataclasses import asdict, dataclass
from logging import getLogger
from typing import ClassVar

from periphery import PWM

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
        self._orientation_worker = Worker(target=self._orientation)

        self._light_worker.start()
        self._orientation_worker.start()

    def _teardown(self) -> None:
        self._light_worker.join()
        self._orientation_worker.join()

    def _light(self) -> None:
        previous_left_indicator_light_status_input = False
        previous_right_indicator_light_status_input = False
        previous_hazard_lights_status_input = False
        previous_daytime_running_lights_status_input = False
        previous_horn_status_input = False
        previous_backup_camera_control_status_input = False
        previous_display_backlight_status_input = False
        previous_brake_lights_status_input = False

        def update_pwm(pwm: PWM, previous_input: bool, input: bool) -> None:
            if not previous_input and input:
                pwm.enable()
            elif previous_input and not input:
                pwm.disable()

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

            update_pwm(
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_left_indicator_light_pwm
                ),
                (
                    previous_left_indicator_light_status_input
                    or previous_hazard_lights_status_input
                ),
                (
                    left_indicator_light_status_input
                    or hazard_lights_status_input
                ),
            )

            update_pwm(
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_right_indicator_light_pwm
                ),
                (
                    previous_right_indicator_light_status_input
                    or previous_hazard_lights_status_input
                ),
                (
                    right_indicator_light_status_input
                    or hazard_lights_status_input
                ),
            )

            update_pwm(
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_indicator_lights_pwm
                ),
                (
                    previous_hazard_lights_status_input
                    or previous_left_indicator_light_status_input
                    or previous_right_indicator_light_status_input
                ),
                (
                    hazard_lights_status_input
                    or left_indicator_light_status_input
                    or right_indicator_light_status_input
                ),
            )

            update_pwm(
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_daytime_running_lights_pwm
                ),
                previous_daytime_running_lights_status_input,
                daytime_running_lights_status_input,
            )

            update_pwm(
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_brake_lights_pwm
                ),
                previous_brake_lights_status_input,
                brake_lights_status_input,
            )

            if horn_status_input != previous_horn_status_input:
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_horn_switch_gpio
                    .write(horn_status_input)
                )

            if (
                    backup_camera_control_status_input
                    != previous_backup_camera_control_status_input
            ):
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_backup_camera_control_switch_gpio
                    .write(backup_camera_control_status_input)
                )

            if (
                    display_backlight_status_input
                    != previous_display_backlight_status_input
            ):
                (
                    self
                    .environment.peripheries
                    .miscellaneous_display_backlight_switch_gpio
                    .write(display_backlight_status_input)
                )

            previous_left_indicator_light_status_input = (
                left_indicator_light_status_input
            )
            previous_right_indicator_light_status_input = (
                right_indicator_light_status_input
            )
            previous_hazard_lights_status_input = hazard_lights_status_input
            previous_daytime_running_lights_status_input = (
                daytime_running_lights_status_input
            )
            previous_brake_lights_status_input = brake_lights_status_input
            previous_horn_status_input = horn_status_input
            previous_backup_camera_control_status_input = (
                backup_camera_control_status_input
            )
            previous_display_backlight_status_input = (
                display_backlight_status_input
            )

    def _orientation(self) -> None:
        while (
                not self._stoppage.wait(
                    (
                        self
                        .environment
                        .settings
                        .miscellaneous_orientation_timeout
                    ),
                )
        ):
            orientation = asdict(
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_orientation_imu_bno055
                    .orientation
                ),
            )

            with self.environment.contexts() as contexts:
                contexts.miscellaneous_orientation.update(orientation)
