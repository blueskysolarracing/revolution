from dataclasses import dataclass
from logging import getLogger
from typing import ClassVar
import time

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
                    contexts.motor_acceleration_cruise_control_input,
                )
                regeneration_input = max(
                    contexts.motor_regeneration_pedal_input,
                    contexts.motor_regeneration_paddle_input,
                    contexts.motor_regeneration_cruise_control_input,
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

    def cruise_control(self) -> None:

        # values from from cruise_control_pi in GEN11_MCMB
        k_p = 250.0
        k_i = 15.0
        k_d = 0.0
        
        integralMin = -200.0
        integralMax = 200.0
        integrator = 0.0

        derivativeMin = -100.0
        derivativeMax = 100.0
        derivative = 0.0

        outMin = -255.0
        outMax = 255.0
        output = 0.0

        timeStep = 0.02
        error = 0.0
        prevError = 0.0

        while (contexts.motor_cruise_control_on):
            error = contexts.motor_cruise_target_speed - contexts.motor_speed
            integrator +=  k_i * ((error + prevError) / 2) * timeStep
            derivative = k_d * (error - prevError) / timeStep

            integrator = np.clip(integrator, integralMin, integralMax)
            derivative = np.clip(derivative, derivativeMin, derivativeMax)

            output = integrator + derivative + k_p * error
            output = np.clip(output, outMin, outMax)

            with self.environment.contexts() as contexts:
                if output >= 0:
                    contexts.motor_acceleration_cruise_control_input = output/outMax
                if output < 0:
                    contexts.motor_regeneration_cruise_control_input = abs(output/outMin)

            prevError = error

            time.sleep(timeStep)