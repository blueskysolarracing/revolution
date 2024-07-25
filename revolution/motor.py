from dataclasses import dataclass
from logging import getLogger
from typing import ClassVar

import numpy as np

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
        self._cruise_control_worker = Worker(target=self._cruise_control)

        self._control_worker.start()
        self._variable_field_magnet_worker.start()
        self._revolution_worker.start()
        self._cruise_control_worker.start()

    def _teardown(self) -> None:
        self._control_worker.join()
        self._variable_field_magnet_worker.join()
        self._revolution_worker.join()
        self._cruise_control_worker.join()

    def _control(self) -> None:
        while (
                not self._stoppage.wait(
                    self.environment.settings.motor_control_timeout,
                )
        ):
            with self.environment.contexts() as contexts:
                status_input = contexts.motor_status_input
                acceleration_input = max(
                    (
                        contexts.motor_acceleration_pedal_input,
                        contexts.motor_acceleration_paddle_input,
                        contexts.motor_acceleration_cruise_control_input,
                    ),
                )
                regeneration_input = max(
                    (
                        contexts.motor_regeneration_pedal_input,
                        contexts.motor_regeneration_paddle_input,
                        contexts.motor_regeneration_cruise_control_input,
                    ),
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
        previous_motor_status = False

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
            motor_status = self.environment.peripheries.motor_mc2.status

            if motor_status and not previous_motor_status:
                (
                    self
                    .environment
                    .peripheries
                    .motor_mc2
                    .variable_field_magnet_reset()
                )

            previous_motor_status = motor_status

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

    def _cruise_control(self) -> None:
        k_p = self.environment.settings.motor_cruise_control_k_p
        k_i = self.environment.settings.motor_cruise_control_k_i
        k_d = self.environment.settings.motor_cruise_control_k_d
        min_integral = (
            self.environment.settings.motor_cruise_control_min_integral
        )
        max_integral = (
            self.environment.settings.motor_cruise_control_max_integral
        )
        min_derivative = (
            self.environment.settings.motor_cruise_control_min_derivative
        )
        max_derivative = (
            self.environment.settings.motor_cruise_control_max_derivative
        )
        min_output = self.environment.settings.motor_cruise_control_min_output
        max_output = self.environment.settings.motor_cruise_control_max_output
        timeout = self.environment.settings.motor_cruise_control_timeout
        integral = 0.0
        error = 0.0

        while not self._stoppage.wait(timeout):
            with self.environment.contexts() as contexts:
                cruise_control_speed = contexts.motor_cruise_control_speed
                motor_speed = contexts.motor_speed

            acceleration_input: float
            regeneration_input: float

            if cruise_control_speed is None:
                integral = 0
                error = 0
                acceleration_input = 0
                regeneration_input = 0
            else:
                previous_error = error
                error = cruise_control_speed - motor_speed
                integral += k_i * (error + previous_error) / 2 * timeout
                derivative = k_d * (error - previous_error) / timeout

                integral = np.clip(integral, min_integral, max_integral)
                derivative = np.clip(
                    derivative,
                    min_derivative,
                    max_derivative,
                )

                output = integral + derivative + k_p * error
                output = np.clip(output, min_output, max_output)

                if output > 0:
                    acceleration_input = output / max_output
                    regeneration_input = 0
                elif output < 0:
                    acceleration_input = 0
                    regeneration_input = abs(output / min_output)
                else:
                    acceleration_input = 0
                    regeneration_input = 0

            with self.environment.contexts() as contexts:
                contexts.motor_acceleration_cruise_control_input = (
                    acceleration_input
                )
                contexts.motor_regeneration_cruise_control_input = (
                    regeneration_input
                )
