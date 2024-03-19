from dataclasses import dataclass
from logging import getLogger
from typing import ClassVar

from revolution.application import Application
from revolution.environment import Endpoint
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
        self._revolution_worker = Worker(target=self._revolution)

        self._control_worker.start()
        self._variable_field_magnet_worker.start()
        self._revolution_worker.start()

    def _teardown(self) -> None:
        self._control_worker.join()
        self._variable_field_magnet_worker.join()
        self._revolution_worker.join()

    def _control(self) -> None:
        while (
                not self._stoppage.wait(
                    self.environment.settings.motor_control_timeout,
                )
        ):
            with self.environment.contexts() as contexts:
                status_input = contexts.motor_status_input
                acceleration_input = max(
                    contexts.motor_acceleration_pedal_input,
                    contexts.motor_acceleration_paddle_input,
                )
                regeneration_input = max(
                    contexts.motor_regeneration_pedal_input,
                    contexts.motor_regeneration_paddle_input,
                )
                direction_input = contexts.motor_direction_input
                economical_mode_input = contexts.motor_economical_mode_input

            self.environment.peripheries.motor_mc2.state(status_input)
            self.environment.peripheries.motor_mc2.accelerate(
                acceleration_input,
            )
            self.environment.peripheries.motor_mc2.regenerate(
                regeneration_input,
            )
            self.environment.peripheries.motor_mc2.direct(direction_input)
            self.environment.peripheries.motor_mc2.economize(
                economical_mode_input,
            )

    def _variable_field_magnet(self) -> None:
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

            if variable_field_magnet_input > 0:
                (
                    self
                    .environment
                    .peripheries
                    .motor_mc2
                    .variable_field_magnet_up()
                )
            elif variable_field_magnet_input < 0:
                (
                    self
                    .environment
                    .peripheries
                    .motor_mc2
                    .variable_field_magnet_down()
                )

    def _revolution(self) -> None:
        while (
                not self._stoppage.wait(
                    self.environment.settings.motor_revolution_timeout,
                )
        ):
            revolution_period = (
                self.environment.peripheries.motor_mc2.revolution_period
            )
            motor_speed = (
                self.environment.settings.motor_wheel_circumference
                / revolution_period
            )

            with self.environment.contexts() as contexts:
                contexts.motor_revolution_period = revolution_period
                contexts.motor_speed = motor_speed
