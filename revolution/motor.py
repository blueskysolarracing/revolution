from dataclasses import dataclass
from logging import getLogger
from math import pi
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
                / self.environment.settings.wheel_diameter
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
                    variable_field_magnet_input = 1
                    contexts.motor_variable_field_magnet_up_input -= 1
                elif contexts.motor_variable_field_magnet_down_input:
                    variable_field_magnet_input = -1
                    contexts.motor_variable_field_magnet_down_input -= 1
                else:
                    variable_field_magnet_input = 0

            if status_input:
                if not previous_status_input:
                    pass  # TODO: variable field magnet reset

                if variable_field_magnet_input > 0:
                    pass  # TODO: variable field magnet up
                elif variable_field_magnet_input < 0:
                    pass  # TODO: variable field magnet down

            previous_status_input = status_input

    def _handle_can(self, message: Message) -> None:

        def rpm2kph(rpm: float) -> float:
            return (
                pi
                * self.environment.settings.wheel_diameter
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
