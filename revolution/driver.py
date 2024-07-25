from dataclasses import dataclass
from logging import getLogger
from typing import ClassVar

from iclib.mcp23s17 import Port, PortRegister as PR, Register

from revolution.application import Application
from revolution.environment import Endpoint
from revolution.worker import Worker

_logger = getLogger(__name__)


@dataclass
class Driver(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.DRIVER
    INPUT_CHANNELS: ClassVar[dict[str, tuple[str, tuple[str, str | None]]]] = {
        # 'driver_motor_acceleration_pedal_input_channel': (
        #     'motor_acceleration_pedal_input',
        #     ('driver_motor_acceleration_pedal_input_range', None),
        # ),
        # 'driver_motor_regeneration_pedal_input_channel': (
        #     'motor_regeneration_pedal_input',
        #     ('driver_motor_regeneration_pedal_input_range', None),
        # ),
        # 'driver_motor_acceleration_paddle_input_channel': (
        #     'motor_acceleration_paddle_input',
        #     ('driver_motor_acceleration_paddle_input_range', None),
        # ),
        # 'driver_motor_regeneration_paddle_input_channel': (
        #     'motor_regeneration_paddle_input',
        #     ('driver_motor_regeneration_paddle_input_range', None),
        # ),

        # 'driver_miscellaneous_thermistor_input_channel': (
        #     'miscellaneous_thermistor_temperature',
        #     (
        #         'driver_miscellaneous_thermistor_input_range',
        #         'driver_miscellaneous_thermistor_output_range',
        #     ),
        # ),
    }
    MOMENTARY_SWITCHES: ClassVar[dict[str, str]] = {
        'driver_motor_direction_switch_prb': (
            'motor_direction_input'
        ),

        # 'driver_miscellaneous_left_indicator_light_switch_prb': (
        #     'miscellaneous_left_indicator_light_status_input'
        # ),
        # 'driver_miscellaneous_right_indicator_light_switch_prb': (
        #     'miscellaneous_right_indicator_light_status_input'
        # ),
        # 'driver_miscellaneous_hazard_lights_switch_prb': (
        #     'miscellaneous_hazard_lights_status_input'
        # ),
        # 'driver_miscellaneous_horn_switch_prb': (
        #     'miscellaneous_horn_status_input'
        # ),
        # 'driver_miscellaneous_brake_pedal_switch_prb': (
        #     'miscellaneous_brake_status_input'
        # ),

        # 'driver_display_steering_wheel_in_place_switch_prb': (
        #     'display_steering_wheel_in_place_status_input'
        # ),
        # 'driver_display_left_directional_pad_switch_prb': (
        #     'display_left_directional_pad_input'
        # ),
        # 'driver_display_right_directional_pad_switch_prb': (
        #     'display_right_directional_pad_input'
        # ),
        # 'driver_display_up_directional_pad_switch_prb': (
        #     'display_up_directional_pad_input'
        # ),
        # 'driver_display_down_directional_pad_switch_prb': (
        #     'display_down_directional_pad_input'
        # ),
        # 'driver_display_center_directional_pad_switch_prb': (
        #     'display_center_directional_pad_input'
        # ),

        'driver_power_battery_relay_switch_prb': (
            'power_battery_relay_status_input'
        ),
        'driver_power_array_relay_switch_prb': (
            'power_array_relay_status_input'
        ),
    }
    TOGGLING_SWITCHES: ClassVar[dict[str, str]] = {
        # 'driver_miscellaneous_daytime_running_lights_switch_prb': (
        #     'miscellaneous_daytime_running_lights_status_input'
        # ),
        # 'driver_miscellaneous_fan_switch_prb': (
        #     'miscellaneous_fan_status_input'
        # ),
        # 'driver_miscellaneous_backup_camera_control_switch_prb': (
        #     'display_backup_camera_control_status_input'
        # ),
    }
    ADDITIVE_SWITCHES: ClassVar[dict[str, str]] = {
        # 'driver_motor_variable_field_magnet_up_switch_prb': (
        #     'motor_variable_field_magnet_up_input'
        # ),
        # 'driver_motor_variable_field_magnet_down_switch_prb': (
        #     'motor_variable_field_magnet_down_input'
        # ),
    }

    def _setup(self) -> None:
        super()._setup()

        self._driver_worker = Worker(target=self._driver)

        self._driver_worker.start()

    def _teardown(self) -> None:
        self._driver_worker.join()

    def _driver(self) -> None:
        previous_lookup = {}

        for i in range(8):
            previous_lookup[Port.PORTA, Register.GPIO, i] = False
            previous_lookup[Port.PORTB, Register.GPIO, i] = False

        while (
                not self._stoppage.wait(
                    self.environment.settings.driver_timeout,
                )
        ):
            gpioa_byte = (
                self.environment.peripheries.driver_mcp23s17.read_register(
                    *PR.GPIOA,
                )[0]
            )
            gpiob_byte = (
                self.environment.peripheries.driver_mcp23s17.read_register(
                    *PR.GPIOB,
                )[0]
            )
            lookup = {}

            for i in range(8):
                lookup[Port.PORTA, Register.GPIO, i] = (
                    not bool(
                        gpioa_byte & (1 << i),
                    )
                )
                lookup[Port.PORTB, Register.GPIO, i] = (
                    not bool(
                        gpiob_byte & (1 << i),
                    )
                )

            voltages = (
                self.environment.peripheries.driver_adc78h89.sample_all()
            )

            with self.environment.contexts() as contexts:
                for (
                        key,
                        (value_name, (input_range_name, output_range_name)),
                ) in self.INPUT_CHANNELS.items():
                    voltage = (
                        voltages[getattr(self.environment.peripheries, key)]
                    )

                    if input_range_name is None:
                        input_range = None
                    else:
                        input_range = getattr(
                            self.environment.settings,
                            input_range_name,
                        )

                    if output_range_name is None:
                        output_range = None
                    else:
                        output_range = getattr(
                            self.environment.settings,
                            output_range_name,
                        )

                    if input_range is not None:
                        voltage = (
                            (voltage - input_range[0])
                            / (input_range[1] - input_range[0])
                        )

                    if output_range is not None:
                        voltage = (
                            voltage * (output_range[1] - output_range[0])
                            + output_range[0]
                        )

                    setattr(contexts, value_name, voltage)

                for key, value in self.MOMENTARY_SWITCHES.items():
                    prb = getattr(self.environment.peripheries, key)

                    setattr(contexts, value, lookup[prb])

                for key, value in self.TOGGLING_SWITCHES.items():
                    prb = getattr(self.environment.peripheries, key)

                    if previous_lookup[prb] != lookup[prb] and lookup[prb]:
                        setattr(contexts, value, not getattr(contexts, value))

                for key, value in self.ADDITIVE_SWITCHES.items():
                    prb = getattr(self.environment.peripheries, key)

                    if previous_lookup[prb] != lookup[prb] and lookup[prb]:
                        setattr(contexts, value, 1 + getattr(contexts, value))

            previous_lookup = lookup
