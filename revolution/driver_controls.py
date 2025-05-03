from collections import defaultdict
from dataclasses import dataclass
from logging import getLogger
from typing import ClassVar

from iclib.mcp23s17 import Port, PortRegister as PR, Register

from revolution.application import Application
from revolution.environment import Endpoint
from revolution.utilities import PRBS
from revolution.worker import Worker

_logger = getLogger(__name__)


@dataclass
class DriverControls(Application):
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
    ROTARY_ENCODERS: ClassVar[
        dict[tuple[str, str], tuple[str, tuple[float, float, float]]]
    ] = {
        (
            'driver_motor_cruise_control_velocity_rotary_encoder_a_prbs',
            'driver_motor_cruise_control_velocity_rotary_encoder_b_prbs',
        ): ('motor_acceleration_input', (30, 180, 1)),
    }
    ANALOG_SIGNALS: ClassVar[dict[str, tuple[str, tuple[float, float]]]] = {
        'driver_motor_acceleration_input_input_channel': (
            'motor_acceleration_input',
            (0, 1),
        ),
    }

    def _setup(self) -> None:
        super()._setup()

        self._driver_worker = Worker(target=self._driver)

        self._driver_worker.start()

    def _teardown(self) -> None:
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
                    not bool(gpioa_byte & (1 << i))
                )
                bytes_[Port.PORTB, Register.GPIO, i] = (
                    not bool(gpiob_byte & (1 << i))
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

            voltages = (
                self
                .environment
                .peripheries
                .driver_pedals_adc78h89
                .sample_all()
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

                if brake_status_input or contexts.motor_acceleration_input:
                    contexts.motor_cruise_control_status_input = False

                for (raw_a_prbs, raw_b_prbs), (value, (min_, max_, step)) in (
                        self.ROTARY_ENCODERS.items()
                ):
                    a_prbs = getattr(self.environment.peripheries, raw_a_prbs)
                    b_prbs = getattr(self.environment.peripheries, raw_b_prbs)
                    direction = 0

                    if previous_lookup[a_prbs] and previous_lookup[b_prbs]:
                        if not lookup[a_prbs] and lookup[b_prbs]:
                            direction = 1
                        elif lookup[a_prbs] and not lookup[b_prbs]:
                            direction = -1

                    if direction:
                        input_ = getattr(contexts, value) + direction * step

                        if input_ < min_:
                            input_ = min_
                        elif input_ > max_:
                            input_ = max_

                        setattr(contexts, value, input_)

                for raw_input_channel, (value, (min_, max_)) in (
                        self.ANALOG_SIGNALS.items()
                ):
                    input_channel = getattr(
                        self.environment.peripheries,
                        raw_input_channel,
                    )
                    voltage = voltages[input_channel]
                    input_ = (voltage - min_) / (max_ - min_)

                    if input_ < min_:
                        input_ = min_
                    elif input_ > max_:
                        input_ = max_

                    setattr(contexts, value, input_)

            previous_lookup = lookup
