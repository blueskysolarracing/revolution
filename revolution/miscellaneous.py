from dataclasses import asdict, dataclass, fields
from datetime import datetime
from logging import getLogger
from os import makedirs
from time import sleep
from typing import ClassVar

from periphery import PWM, I2CError

from iclib.bno055 import OperationMode, Register, Unit
from iclib.lis2hh12 import LIS2HH12
from revolution.application import Application
from revolution.environment import Contexts, Endpoint
from revolution.worker import Worker

_logger = getLogger(__name__)


@dataclass
class Miscellaneous(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.MISCELLANEOUS

    def _setup(self) -> None:
        super()._setup()

        self._light_worker = Worker(target=self._light)
        self._indicator_light_worker = Worker(target=self._indicator_light)
        self._imu_worker = Worker(target=self._imu)
        self._gps_worker = Worker(target=self._gps)
        self._front_wheels_worker = Worker(target=self._front_wheels)
        self._runtime_log_worker = Worker(target=self._runtime_log)

        self._light_worker.start()
        self._indicator_light_worker.start()
        self._imu_worker.start()
        self._gps_worker.start()
        # self._front_wheels_worker.start()
        self._runtime_log_worker.start()

    def _teardown(self) -> None:
        self._light_worker.join()
        self._indicator_light_worker.join()
        self._imu_worker.join()
        self._gps_worker.join()
        # self._front_wheels_worker.join()
        self._runtime_log_worker.join()

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

            steering_wheel = self.environment.peripheries.driver_steering_wheel
            steering_wheel.set_indicator_light(
                (
                    (
                        left_indicator_light_status_input
                        or hazard_lights_status_input
                    )
                    and flash_status
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

    def _imu(self) -> None:
        def imu_config() -> None:
            self.environment.peripheries.miscellaneous_imu_bno055.reset2()
            self.environment.peripheries.miscellaneous_imu_bno055.write(
                Register.OPR_MODE,
                0x00
            )
            sleep(self.environment.settings.miscellaneous_imu_mode_timeout)
            self.environment.peripheries.miscellaneous_imu_bno055.select_units(
                Unit.MS2,
                Unit.DPS,
                Unit.DEGREES,
                Unit.CELSIUS
            )
            sleep(self.environment.settings.miscellaneous_imu_mode_timeout)
            self.environment.peripheries.miscellaneous_imu_bno055.write(
                Register.OPR_MODE,
                OperationMode.IMU
            )
            sleep(self.environment.settings.miscellaneous_imu_mode_timeout)

        imu_working = False
        previous_imu_working = False

        while (
                not self._stoppage.wait(
                    (
                        self
                        .environment
                        .settings
                        .miscellaneous_imu_timeout
                    ),
                )
        ):
            previous_imu_working = imu_working

            if previous_imu_working:
                try:
                    bno055 = (
                        self.environment.peripheries.miscellaneous_imu_bno055
                    )
                    orientation = asdict(bno055.orientation)
                    angular_velocity = asdict(bno055.angular_velocity)
                    linear_acceleration = asdict(bno055.linear_acceleration)

                    with self.environment.contexts() as contexts:
                        contexts.miscellaneous_orientation.update(orientation)
                        contexts.miscellaneous_angular_velocity.update(
                            angular_velocity,
                        )
                        contexts.miscellaneous_linear_acceleration.update(
                            linear_acceleration,
                        )

                    imu_working = True
                except I2CError:
                    imu_working = False
            else:
                try:
                    imu_config()
                    imu_working = True
                except I2CError:
                    imu_working = False

            with self.environment.contexts() as contexts:
                contexts.miscellaneous_imu_working = imu_working

    def _gps(self) -> None:
        periphery = self.environment.peripheries.miscellaneous_gps
        periphery.send_command(
            b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'
        )
        periphery.send_command(b'PMTK220,1000')

        while (
                not self._stoppage.wait(
                    (
                        self
                        .environment
                        .settings
                        .miscellaneous_gps_timeout
                    ),
                )
        ):
            periphery.update()

            with self.environment.contexts() as contexts:
                if periphery.has_fix:
                    if periphery.latitude is not None:
                        contexts.miscellaneous_latitude = periphery.latitude
                    if periphery.longitude is not None:
                        contexts.miscellaneous_longitude = periphery.longitude
                    if periphery.altitude_m is not None:
                        contexts.miscellaneous_altitude = periphery.altitude_m
                if periphery.fix_quality is not None:
                    contexts.miscellaneous_gps_fix_quality = (
                        periphery.fix_quality
                    )
                if periphery.fix_quality_3d is not None:
                    contexts.miscellaneous_gps_fix_quality_3d = (
                        periphery.fix_quality_3d
                    )
                if periphery.satellites is not None:
                    contexts.miscellaneous_gps_satellites = (
                        periphery.satellites
                    )

    def _front_wheels(self) -> None:
        def left_accelerometer_config() -> None:
            (
                self
                .environment
                .peripheries
                .miscellaneous_front_wheels_i2c_mux.channel_select([0, 1])
            )
            (
                self
                .environment
                .peripheries
                .miscellaneous_left_wheel_accelerometer.config(
                    odr=100,
                    measurement_range=8,
                    enable_axes=True,
                    enable_auto_inc=True
                )
            )

        def right_accelerometer_config() -> None:
            (
                self
                .environment
                .peripheries
                .miscellaneous_front_wheels_i2c_mux.channel_select([0, 1])
            )
            (
                self
                .environment
                .peripheries
                .miscellaneous_right_wheel_accelerometer.config(
                    odr=100,
                    measurement_range=8,
                    enable_axes=True,
                    enable_auto_inc=True
                )
            )

        @dataclass
        class FrontWheelLogData:
            miscellaneous_left_wheel_accelerations: list[float]
            miscellaneous_right_wheel_accelerations: list[float]
            miscellaneous_orientation: dict[str, float]
            miscellaneous_angular_velocity: dict[str, float]
            miscellaneous_linear_acceleration: dict[str, float]

        left_wheel_accel_working = False
        right_wheel_accel_working = False
        previous_left_wheel_accel_working = False
        previous_right_wheel_accel_working = False

        filepath = (
            self.environment.settings.general_log_filepath
        )

        print_log = filepath != ''

        if print_log:
            filepath += 'front_wheel_log/'
            makedirs(filepath, exist_ok=True)
            now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            log_file = open(f'{filepath}{now}_front_wheel_log.csv', 'w')
            print('time, ', end='', file=log_file)
            with self.environment.contexts() as contexts:
                for field in fields(FrontWheelLogData):
                    if isinstance(getattr(contexts, field.name), dict):
                        for k in getattr(contexts, field.name).keys():
                            print(f'{field.name}.{k}, ', end='', file=log_file)
                    elif isinstance(getattr(contexts, field.name), list):
                        for i in range(len(getattr(contexts, field.name))):
                            print(f'{field.name}.{i}, ', end='', file=log_file)
                    else:
                        print(f'{field.name}, ', end='', file=log_file)

            print(file=log_file)
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
            previous_left_wheel_accel_working = left_wheel_accel_working
            previous_right_wheel_accel_working = right_wheel_accel_working

            left_accel = LIS2HH12.Vector(0.0, 0.0, 0.0)
            if previous_left_wheel_accel_working:
                try:
                    left_accel = (
                        self
                        .environment
                        .peripheries
                        .miscellaneous_left_wheel_accelerometer
                        .read_acceleration()
                    )
                    with self.environment.contexts() as contexts:
                        contexts.miscellaneous_left_wheel_accelerations = [
                            left_accel.x,
                            left_accel.y,
                            left_accel.z,
                        ]
                        left_wheel_accel_working = True
                except I2CError:
                    left_wheel_accel_working = False
            else:
                try:
                    left_accelerometer_config()
                    left_wheel_accel_working = True
                except I2CError:
                    left_wheel_accel_working = False

            right_accel = LIS2HH12.Vector(0.0, 0.0, 0.0)
            if previous_right_wheel_accel_working:
                try:
                    right_accel = (
                        self
                        .environment
                        .peripheries
                        .miscellaneous_right_wheel_accelerometer
                        .read_acceleration()
                    )
                    with self.environment.contexts() as contexts:
                        contexts.miscellaneous_right_wheel_accelerations = [
                            right_accel.x,
                            right_accel.y,
                            right_accel.z,
                        ]
                        right_wheel_accel_working = True
                except I2CError:
                    right_wheel_accel_working = False
            else:
                try:
                    right_accelerometer_config()
                    right_wheel_accel_working = True
                except I2CError:
                    right_wheel_accel_working = False

            with self.environment.contexts() as contexts:
                contexts.miscellaneous_left_wheel_accelerometer_working = (
                    left_wheel_accel_working
                )
                contexts.miscellaneous_right_wheel_accelerometer_working = (
                    right_wheel_accel_working
                )

            if not print_log:
                continue

            print(f'{datetime.now().time()}, ', end='', file=log_file)
            with self.environment.contexts() as contexts:
                for field in fields(FrontWheelLogData):
                    if isinstance(getattr(contexts, field.name), dict):
                        for value in getattr(contexts, field.name).values():
                            print(f'{value}, ', end='', file=log_file)
                    elif isinstance(getattr(contexts, field.name), list):
                        for i in range(len(getattr(contexts, field.name))):
                            value = getattr(contexts, field.name)[i]
                            print(f'{value}, ', end='', file=log_file)
                    else:
                        value = getattr(contexts, field.name)
                        print(f'{value}, ', end='', file=log_file)

            print(file=log_file)
            log_file.flush()

        if print_log:
            log_file.close()

    def _runtime_log(self) -> None:
        filepath = (
            self.environment.settings.general_log_filepath
        )

        print_log = filepath != ''

        if not print_log:
            return

        filepath += 'runtime_log/'
        makedirs(filepath, exist_ok=True)
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = open(f'{filepath}{now}_runtime_log.csv', 'w')

        print('time, ', end='', file=log_file)
        with self.environment.contexts() as contexts:
            for field in fields(Contexts):
                if isinstance(getattr(contexts, field.name), dict):
                    for key in getattr(contexts, field.name).keys():
                        print(f'{field.name}.{key}, ', end='', file=log_file)
                elif isinstance(getattr(contexts, field.name), list):
                    for i in range(len(getattr(contexts, field.name))):
                        print(f'{field.name}.{i}, ', end='', file=log_file)
                else:
                    print(f'{field.name}, ', end='', file=log_file)
        print(file=log_file)
        log_file.flush()

        while (
                not self._stoppage.wait(
                    (
                        self
                        .environment
                        .settings
                        .power_log_timeout
                    ),
                )
        ):
            print(f'{datetime.now().time()}, ', end='', file=log_file)
            with self.environment.contexts() as contexts:
                for field in fields(Contexts):
                    if isinstance(getattr(contexts, field.name), dict):
                        for value in getattr(contexts, field.name).values():
                            if isinstance(value, float):
                                value = f'{value:.3f}'
                            elif isinstance(value, bool):
                                value = 'T' if value else 'F'
                            print(f'{value}, ', end='', file=log_file)
                    elif isinstance(getattr(contexts, field.name), list):
                        for i in range(len(getattr(contexts, field.name))):
                            value = getattr(contexts, field.name)[i]
                            if isinstance(value, float):
                                value = f'{value:.3f}'
                            elif isinstance(value, bool):
                                value = 'T' if value else 'F'
                            print(f'{value}, ', end='', file=log_file)
                    else:
                        value = getattr(contexts, field.name)
                        if isinstance(value, float):
                            value = f'{value:.3f}'
                        elif isinstance(value, bool):
                            value = 'T' if value else 'F'
                        print(f'{value}, ', end='', file=log_file)
            print(file=log_file)
            log_file.flush()

        log_file.close()
