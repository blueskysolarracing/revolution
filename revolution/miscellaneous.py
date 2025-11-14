from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime
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
        self._indicator_light_worker = Worker(target=self._indicator_light)
        self._orientation_worker = Worker(target=self._orientation)
        self._position_worker = Worker(target=self._position)
        self._front_wheels_worker = Worker(target=self._front_wheels)

        self._light_worker.start()
        self._indicator_light_worker.start()
        self._orientation_worker.start()
        self._position_worker.start()
        self._front_wheels_worker.start()

    def _teardown(self) -> None:
        self._light_worker.join()
        self._indicator_light_worker.join()
        self._orientation_worker.join()
        self._position_worker.join()
        self._front_wheels_worker.join()

    def update_pwm(self, pwm: PWM, previous_input: bool, input: bool) -> None:
        if not previous_input and input:
            pwm.enable()
        elif previous_input and not input:
            pwm.disable()

    def _light(self) -> None:
        previous_daytime_running_lights_status_input = False
        previous_horn_status_input = False
        previous_backup_camera_control_status_input = False
        previous_brake_lights_status_input = False

        while (
                not self._stoppage.wait(
                    self.environment.settings.miscellaneous_light_timeout,
                )
        ):
            with self.environment.contexts() as contexts:
                daytime_running_lights_status_input = (
                    contexts.miscellaneous_daytime_running_lights_status_input
                )
                horn_status_input = contexts.miscellaneous_horn_status_input
                backup_camera_control_status_input = (
                    contexts.miscellaneous_backup_camera_control_status_input
                )
                brake_lights_status_input = (
                    contexts.miscellaneous_brake_status_input
                    or contexts.motor_regeneration_status_input
                )

            self.update_pwm(
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_daytime_running_lights_pwm
                ),
                previous_daytime_running_lights_status_input,
                daytime_running_lights_status_input,
            )

            self.update_pwm(
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
                    .power_battery_management_system
                    .update_horn(horn_status_input)
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

            previous_daytime_running_lights_status_input = (
                daytime_running_lights_status_input
            )
            previous_brake_lights_status_input = brake_lights_status_input
            previous_horn_status_input = horn_status_input
            previous_backup_camera_control_status_input = (
                backup_camera_control_status_input
            )

    def _indicator_light(self) -> None:
        previous_left_indicator_light_status_input = False
        previous_right_indicator_light_status_input = False
        previous_hazard_lights_status_input = False
        previous_flash_status = False
        flash_status = False

        while (
                not self._stoppage.wait(
                    self
                    .environment
                    .settings
                    .miscellaneous_light_flash_timeout,
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

            flash_status = not flash_status

            self.update_pwm(
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_left_indicator_light_pwm
                ),
                (
                    (
                        previous_left_indicator_light_status_input
                        or previous_hazard_lights_status_input
                    )
                    and previous_flash_status
                ),
                (
                    (
                        left_indicator_light_status_input
                        or hazard_lights_status_input
                    )
                    and flash_status
                ),
            )

            self.update_pwm(
                (
                    self
                    .environment
                    .peripheries
                    .miscellaneous_right_indicator_light_pwm
                ),
                (
                    (
                        previous_right_indicator_light_status_input
                        or previous_hazard_lights_status_input
                    )
                    and previous_flash_status
                ),
                (
                    (
                        right_indicator_light_status_input
                        or hazard_lights_status_input
                    )
                    and flash_status
                ),
            )

            previous_left_indicator_light_status_input = (
                left_indicator_light_status_input
            )
            previous_right_indicator_light_status_input = (
                right_indicator_light_status_input
            )
            previous_hazard_lights_status_input = hazard_lights_status_input
            previous_flash_status = flash_status

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

    def _position(self) -> None:
        while (
                not self._stoppage.wait(
                    (
                        self
                        .environment
                        .settings
                        .miscellaneous_position_timeout
                    ),
                )
        ):
            periphery = (
                self
                .environment
                .peripheries
                .miscellaneous_position_gps
            )

            periphery.update()

            if not periphery.has_fix:
                with self.environment.contexts() as contexts:
                    contexts.miscellaneous_latitude = periphery.latitude
                    contexts.miscellaneous_longitude = periphery.longitude

    def _front_wheels(self) -> None:
        (
            self
            .environment
            .peripheries
            .miscellaneous_left_wheel_accelerometer.config()
        )

        (
            self
            .environment
            .peripheries
            .miscellaneous_right_wheel_accelerometer.config()
        )

        filepath = self.environment.settings.general_log_filepath
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = open(f'{filepath}{now}_front_wheel_log.csv', "w")
        print(
            'time, left.x, left.y, left.z, right.x, right.y, right.z, '
            'imu.x, imu.y, imu.z',
            file=log_file,
        )
        log_file.flush()

        while (
                not self._stoppage.wait(
                    (
                        self
                        .environment
                        .settings
                        .miscellaneous_front_wheels_timeout
                    ),
                )
        ):
            left_accel = (
                self
                .environment
                .peripheries
                .miscellaneous_left_wheel_accelerometer
                .read_accel()
            )
            right_accel = (
                self
                .environment
                .peripheries
                .miscellaneous_right_wheel_accelerometer
                .read_accel()
            )
            imu = {}

            with self.environment.contexts() as contexts:
                contexts.miscellaneous_left_wheel_accelerations = [
                    left_accel.x,
                    left_accel.y,
                    left_accel.z,
                ]
                contexts.miscellaneous_right_wheel_accelerations = [
                    right_accel.x,
                    right_accel.y,
                    right_accel.z,
                ]
                imu = deepcopy(contexts.miscellaneous_orientation)

            print(f'{datetime.now().time()}, '
                  f'{left_accel.x}, {left_accel.y}, {left_accel.z}, '
                  f'{right_accel.x}, {right_accel.y}, {right_accel.z}, '
                  f'{imu.get('x', -100)}, {imu.get('y', -100)}, '
                  f'{imu.get('z', -100)}',
                  file=log_file
            )
            log_file.flush()
