from collections import defaultdict
from dataclasses import dataclass
from logging import getLogger
from typing import ClassVar

from iclib.mcp23s17 import Port, PortRegister as PR, Register
from iclib.rotary_encoder import RotaryEncoder

from revolution.application import Application
from revolution.environment import Endpoint
from revolution.utilities import PRBS
from revolution.worker import Worker

_logger = getLogger(__name__)


@dataclass
class Driver(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.DRIVER
    MOMENTARY_SWITCHES: ClassVar[dict[str, str]] = {
        'driver_miscellaneous_left_indicator_light_switch_prbs': (
            'miscellaneous_left_indicator_light_status_input'
        ),
        'driver_miscellaneous_right_indicator_light_switch_prbs': (
            'miscellaneous_right_indicator_light_status_input'
        ),
        'driver_miscellaneous_horn_switch_prbs': (
            'miscellaneous_horn_status_input'
        ),

        'driver_motor_direction_switch_prbs': (
            'motor_direction_input'
        ),
        'driver_motor_regeneration_switch_prbs': (
            'motor_regeneration_input'
        ),

        'driver_power_array_relay_switch_prbs': (
            'power_array_relay_status_input'
        ),
        'driver_power_battery_relay_switch_prbs': (
            'power_battery_relay_status_input'
        ),
    }
    TOGGLING_SWITCHES: ClassVar[dict[str, str]] = {
        'driver_miscellaneous_hazard_lights_switch_prbs': (
            'miscellaneous_hazard_lights_status_input'
        ),
        'driver_miscellaneous_daytime_running_lights_switch_prbs': (
            'miscellaneous_daytime_running_lights_status_input'
        ),
        'driver_miscellaneous_backup_camera_control_switch_prbs': (
            'miscellaneous_backup_camera_control_status_input'
        ),
        'driver_miscellaneous_display_backlight_switch_prbs': (
            'miscellaneous_display_backlight_status_input'
        ),
        'driver_motor_cruise_control_switch_prbs': (
            'motor_cruise_control_status_input'
        ),
    }
    ADDITIVE_SWITCHES: ClassVar[dict[str, str]] = {
        'driver_motor_variable_field_magnet_up_switch_prbs': (
            'motor_variable_field_magnet_up_input'
        ),
        'driver_motor_variable_field_magnet_down_switch_prbs': (
            'motor_variable_field_magnet_down_input'
        ),
    }

    def _setup(self) -> None:
        super()._setup()

        def callback(direction: RotaryEncoder.Direction) -> None:
            with self.environment.contexts() as contexts:
                acceleration_input = contexts.motor_acceleration_input
                acceleration_input += (
                    direction
                    * self.environment.settings.driver_acceleration_input_step
                )

                if acceleration_input < 0:
                    acceleration_input = 0
                elif acceleration_input > 1:
                    acceleration_input = 1

                contexts.motor_acceleration_input = acceleration_input

        self._rotary_encoder = RotaryEncoder(
            (
                self
                .environment
                .peripheries
                .driver_motor_acceleration_input_rotary_encoder_a_gpio
            ),
            (
                self
                .environment
                .peripheries
                .driver_motor_acceleration_input_rotary_encoder_b_gpio
            ),
            callback,
            self.environment.settings.driver_timeout,
        )

        self._driver_worker = Worker(target=self._driver)

        self._driver_worker.start()

    def _teardown(self) -> None:
        self._rotary_encoder.stop()
        self._driver_worker.join()

    def _driver(self) -> None:
        previous_lookup = defaultdict[PRBS, bool](bool)

        while (
                not self._stoppage.wait(
                    self.environment.settings.driver_timeout,
                )
        ):
            gpioa_byte = (
                self
                .environment
                .peripheries
                .driver_steering_wheel_mcp23s17
                .read_register(*PR.GPIOA)[0]
            )
            gpiob_byte = (
                self
                .environment
                .peripheries
                .driver_steering_wheel_mcp23s17
                .read_register(*PR.GPIOB)[0]
            )
            bytes_ = {}

            for i in range(8):
                bytes_[Port.PORTA, Register.GPIO, i] = (
                    not bool(
                        gpioa_byte & (1 << i),
                    )
                )
                bytes_[Port.PORTB, Register.GPIO, i] = (
                    not bool(
                        gpiob_byte & (1 << i),
                    )
                )

            shift = bytes_.get(
                self.environment.peripheries.driver_shift_switch_prb,
                False,
            )
            lookup = defaultdict[PRBS, bool](bool)

            for prb, bit in bytes_.items():
                lookup[prb] = bit
                lookup[prb, shift] = bit

            brake_status_input = (
                self
                .environment
                .peripheries
                .driver_miscellaneous_brake_switch_gpio
                .read()
            )

            with self.environment.contexts() as contexts:
                for raw_prbs, value in self.MOMENTARY_SWITCHES.items():
                    prbs = getattr(self.environment.peripheries, raw_prbs)

                    setattr(contexts, value, lookup[prbs])

                for raw_prbs, value in self.TOGGLING_SWITCHES.items():
                    prbs = getattr(self.environment.peripheries, raw_prbs)

                    if not previous_lookup[prbs] and lookup[prbs]:
                        setattr(contexts, value, not getattr(contexts, value))

                for raw_prbs, value in self.ADDITIVE_SWITCHES.items():
                    prbs = getattr(self.environment.peripheries, raw_prbs)

                    if not previous_lookup[prbs] and lookup[prbs]:
                        setattr(contexts, value, 1 + getattr(contexts, value))

                contexts.miscellaneous_brake_status_input = brake_status_input

            previous_lookup = lookup
