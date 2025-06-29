from dataclasses import dataclass
from logging import getLogger
from math import pi
from time import sleep, time
from typing import ClassVar

from can import Message
from iclib.wavesculptor22 import VelocityMeasurement

from revolution.application import Application
from revolution.environment import Endpoint
from revolution.utilities import Direction
from revolution.worker import Worker

_logger = getLogger(__name__)


@dataclass
class Motor(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.MOTOR

    def _setup(self) -> None:
        super()._setup()

        self._control_worker = Worker(target=self._control)
        self._variable_field_magnet_worker = Worker(
            target=self._variable_field_magnet,
        )

        self._control_worker.start()
        self._variable_field_magnet_worker.start()

    def _teardown(self) -> None:
        self._control_worker.join()
        self._variable_field_magnet_worker.join()

    def _control(self) -> None:

        def kph2rpm(kph: float) -> float:
            return (
                kph
                / pi
                / self.environment.settings.general_wheel_diameter
                / 60
                * 1000
            )

        previous_status_input = False

        while (
                not self._stoppage.wait(
                    self.environment.settings.motor_control_timeout,
                )
        ):
            with self.environment.contexts() as contexts:
                status_input = contexts.motor_status_input
                acceleration_input = contexts.motor_acceleration_input
                direction_input = contexts.motor_direction_input
                cruise_control_status_input = (
                    contexts.motor_cruise_control_status_input
                )
                cruise_control_velocity = (
                    contexts.motor_cruise_control_velocity
                )
                brake_status_input = contexts.miscellaneous_brake_status_input

            if status_input:
                if not previous_status_input:
                    self.environment.peripheries.motor_wavesculptor22.reset()
                else:
                    (
                        self
                        .environment
                        .peripheries
                        .motor_wavesculptor22
                        .motor_power(1)
                    )

                    if direction_input == Direction.BACKWARD:
                        acceleration_input *= -1
                        cruise_control_velocity *= -1

                    if cruise_control_status_input:
                        (
                            self
                            .environment
                            .peripheries
                            .motor_wavesculptor22
                            .motor_drive_velocity_control_mode(
                                kph2rpm(cruise_control_velocity),
                            )
                        )
                    else:
                        if brake_status_input:
                            (
                                self
                                .environment
                                .peripheries
                                .motor_wavesculptor22
                                .motor_drive(1, 0)
                            )
                        elif acceleration_input == 0:
                            regeneration_strength = (
                                self
                                .environment
                                .settings
                                .motor_regeneration_strength
                            )
                            (
                                self
                                .environment
                                .peripheries
                                .motor_wavesculptor22
                                .motor_drive(regeneration_strength, 0)
                            )
                        else:
                            (
                                self
                                .environment
                                .peripheries
                                .motor_wavesculptor22
                                .motor_drive_torque_control_mode(
                                    acceleration_input,
                                )
                            )

            previous_status_input = status_input

    def _variable_field_magnet(self) -> None:
        previous_status_input = False
        previous_direction = Direction.FORWARD

        step_size = (
            self.environment.settings.motor_variable_field_magnet_step_size
        )
        step_upper_limit = (
            self
            .environment
            .settings.motor_variable_field_magnet_step_upper_limit
        )
        frequency = (
            self.environment.settings.motor_variable_field_magnet_frequency
        )
        duty_cycle = (
            self.environment.settings.motor_variable_field_magnet_duty_cycle
        )
        delay_high = 1.0 / frequency * duty_cycle
        delay_low = 1.0 / frequency * (1 - duty_cycle)
        stall_threshold = (
            self
            .environment
            .settings
            .motor_variable_field_magnet_stall_threshold
        )
        max_enable_time = (
            self
            .environment
            .settings
            .motor_variable_field_magnet_max_enable_time
        )
        print("vfm start")

        while (
                not self._stoppage.wait(
                    (
                        self
                        .environment
                        .settings
                        .motor_variable_field_magnet_timeout
                    ),
                )
        ):
            with self.environment.contexts() as contexts:
                status_input = contexts.motor_status_input
                min_value = min(
                    contexts.motor_variable_field_magnet_up_input,
                    contexts.motor_variable_field_magnet_down_input,
                )
                contexts.motor_variable_field_magnet_up_input -= min_value
                contexts.motor_variable_field_magnet_down_input -= min_value

                if contexts.motor_variable_field_magnet_up_input:
                    input_ = 1
                    contexts.motor_variable_field_magnet_up_input -= 1
                elif contexts.motor_variable_field_magnet_down_input:
                    input_ = -1
                    contexts.motor_variable_field_magnet_down_input -= 1
                else:
                    input_ = 0

                position = contexts.motor_variable_field_magnet_position

            if status_input:
                if not previous_status_input:
                    print("vfm reset")
                    position = 0
                    stall_count = 0
                    start_time = time()

                    (
                        self
                        .environment
                        .peripheries
                        .motor_variable_field_magnet_direction_gpio
                        .write(bool(Direction.FORWARD))
                    )

                    while (
                            stall_count < stall_threshold
                            and (time() - start_time) < max_enable_time
                    ):
                        if (
                                (
                                    self
                                    .environment
                                    .peripheries
                                    .motor_variable_field_magnet_stall_gpio
                                    .read()
                                )
                        ):
                            stall_count += 1

                        (
                            self
                            .environment
                            .peripheries
                            .motor_variable_field_magnet_enable_gpio
                            .write(True)
                        )
                        sleep(delay_high)
                        (
                            self
                            .environment
                            .peripheries
                            .motor_variable_field_magnet_enable_gpio
                            .write(False)
                        )
                        sleep(delay_low)

                    (
                        self
                        .environment
                        .peripheries
                        .motor_variable_field_magnet_enable_gpio
                        .write(False)
                    )

                    previous_direction = Direction.FORWARD

                if input_ > 0 and (position + step_size) <= step_upper_limit:
                    direction = Direction.BACKWARD
                    position += step_size
                elif input_ < 0 and (position - step_size) >= 0:
                    direction = Direction.FORWARD
                    position -= step_size
                else:
                    direction = None

                if direction is not None:
                    print("vfm move")
                    (
                        self
                        .environment
                        .peripheries
                        .motor_variable_field_magnet_direction_gpio
                        .write(bool(direction))
                    )

                    step_count = step_size
                    stall_count = 0
                    start_time = time()

                    if direction != previous_direction:
                        step_count += 1

                    while (
                            step_count
                            and stall_count < stall_threshold
                            and (time() - start_time) < max_enable_time
                    ):
                        if (
                                (
                                    self
                                    .environment
                                    .peripheries
                                    .motor_variable_field_magnet_stall_gpio
                                    .read()
                                )
                        ):
                            stall_count += 1

                        if (
                                (
                                    self
                                    .environment
                                    .peripheries
                                    .motor_variable_field_magnet_encoder_a_gpio
                                    .poll(0)
                                )
                        ):
                            (
                                self
                                .environment
                                .peripheries
                                .motor_variable_field_magnet_encoder_a_gpio
                                .read_event()
                            )
                            step_count -= 1

                        (
                            self
                            .environment
                            .peripheries
                            .motor_variable_field_magnet_enable_gpio
                            .write(True)
                        )
                        sleep(delay_high)
                        (
                            self
                            .environment
                            .peripheries
                            .motor_variable_field_magnet_enable_gpio
                            .write(False)
                        )
                        sleep(delay_low)

                    (
                        self
                        .environment
                        .peripheries
                        .motor_variable_field_magnet_enable_gpio
                        .write(False)
                    )

                    previous_direction = direction

                with self.environment.contexts() as contexts:
                    contexts.motor_variable_field_magnet_position = (
                        position
                    )

            previous_status_input = status_input

    def _handle_can(self, message: Message) -> None:

        def rpm2kph(rpm: float) -> float:
            return (
                pi
                * self.environment.settings.general_wheel_diameter
                * rpm
                * 60
                / 1000
            )

        super()._handle_can(message)

        broadcast_message = (
            self.environment.peripheries.motor_wavesculptor22.parse(message)
        )

        if broadcast_message is None:
            return

        with self.environment.contexts() as contexts:
            if isinstance(broadcast_message, VelocityMeasurement):
                contexts.motor_velocity = rpm2kph(
                    broadcast_message.motor_velocity,
                )

            contexts.motor_heartbeat_timestamp = time()
