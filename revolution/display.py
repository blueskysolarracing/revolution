from dataclasses import dataclass
from logging import getLogger
from typing import ClassVar

from revolution.application import Application
from revolution.battery_management_system import BatteryFlag
from revolution.environment import Endpoint
from revolution.worker import Worker

_logger = getLogger(__name__)


@dataclass
class Display(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.DISPLAY

    def _setup(self) -> None:
        super()._setup()

        periphery = (
            self.environment.peripheries.display_nhd_c12864a1z_fsw_fbw_htt
        )

        periphery.set_font(self.environment.settings.display_font_pathname)

        self._display_worker = Worker(target=self._display)

        self._display_worker.start()

    def _teardown(self) -> None:
        self._display_worker.join()

    def _display(self) -> None:
        timeout = 1 / self.environment.settings.display_frame_rate

        while not self._stoppage.wait(timeout):
            with self.environment.contexts() as contexts:
                miscellaneous_left_indicator_light_status = (
                    contexts.miscellaneous_left_indicator_light_status_input
                )
                miscellaneous_right_indicator_light_status = (
                    contexts.miscellaneous_right_indicator_light_status_input
                )
                miscellaneous_hazard_lights_status = (
                    contexts.miscellaneous_hazard_lights_status_input
                )
                motor_velocity = contexts.motor_velocity
                motor_cruise_control_status_input = (
                    contexts.motor_cruise_control_status_input
                )
                motor_cruise_control_velocity = (
                    contexts.motor_cruise_control_velocity
                )
                motor_variable_field_magnet_position = (
                    contexts.motor_variable_field_magnet_position
                )
                power_battery_state_of_charge = (
                    contexts.power_battery_mean_state_of_charge
                )
                power_battery_discharge_status = (
                    contexts.power_battery_discharge_status
                )
                power_battery_min_cell_voltage = (
                    contexts.power_battery_min_cell_voltage
                )
                power_battery_max_cell_voltage = (
                    contexts.power_battery_max_cell_voltage
                )
                power_battery_current = (
                    contexts.power_battery_current
                )
                power_battery_min_thermistor_temperature = (
                    contexts.power_battery_min_thermistor_temperature
                )
                power_battery_max_thermistor_temperature = (
                    contexts.power_battery_max_thermistor_temperature
                )
                power_battery_flags_hold = (
                    contexts.power_battery_flags_hold
                )

            periphery = (
                self.environment.peripheries.display_nhd_c12864a1z_fsw_fbw_htt
            )

            periphery.clear_screen(False)

            # Miscellaneous

            if miscellaneous_left_indicator_light_status:
                periphery.set_size(10, 12)
                periphery.draw_word('<', 5, 4)

            if miscellaneous_right_indicator_light_status:
                periphery.set_size(10, 12)
                periphery.draw_word('>', 18, 4)

            if miscellaneous_hazard_lights_status:
                periphery.set_size(6, 12)
                periphery.draw_word('(', 31, 4)
                periphery.set_size(9, 12)
                periphery.draw_word('!!', 38, 4)
                periphery.set_size(6, 12)
                periphery.draw_word(')', 52, 4)

            # Motor

            periphery.set_size(18, 24)
            periphery.draw_word(f'{motor_velocity:3.0f}', 23, 20)
            periphery.set_size(8, 15)
            # periphery.draw_word('KM/H', 78, 27)

            motor_cruise_control_label = (
                'ON' if motor_cruise_control_status_input else 'OFF'
            )

            periphery.set_size(6, 12)
            periphery.draw_word(
                (
                    f'CC ({motor_cruise_control_label}):'
                    f' {motor_cruise_control_velocity:.0f} '
                ),
                7,
                49,
            )

            motor_variable_field_magnet_step = (
                motor_variable_field_magnet_position
                / (
                        self
                        .environment
                        .settings
                        .motor_variable_field_magnet_step_size
                )
            )

            periphery.draw_word(
                (f'VFM:{motor_variable_field_magnet_step:1.0f}'), 93, 49,
            )

            # Power

            periphery.set_size(8, 12)
            periphery.draw_word(
                f'{power_battery_state_of_charge * 100:3.0f}%',
                93,
                4,
            )

            periphery.set_size(6, 8)
            periphery.draw_word('V', 85, 18)
            periphery.draw_word(
                f'{power_battery_min_cell_voltage * 10:2.0f}',
                95,
                18,
            )
            periphery.write_pixel(99, 26)

            periphery.draw_word(
                f'{power_battery_max_cell_voltage * 10:2.0f}',
                112,
                18,
            )
            periphery.write_pixel(116, 26)

            periphery.draw_word('T', 85, 28)
            periphery.draw_word(
                f'{power_battery_min_thermistor_temperature:2.0f}',
                95,
                28,
            )

            periphery.draw_word(
                f'{power_battery_max_thermistor_temperature:2.0f}',
                112,
                28,
            )

            periphery.draw_word('I', 85, 38)
            periphery.draw_word(
                f'{power_battery_current:2.0f}',
                112,
                38,
            )

            if (power_battery_flags_hold & BatteryFlag.OVERVOLTAGE):
                periphery.write_pixel(83, 18)
            if (power_battery_flags_hold & BatteryFlag.UNDERVOLTAGE):
                periphery.write_pixel(83, 25)
            if (power_battery_flags_hold & BatteryFlag.OVERTEMPERATURE):
                periphery.write_pixel(83, 28)
            if (power_battery_flags_hold & BatteryFlag.UNDERTEMPERATURE):
                periphery.write_pixel(83, 35)
            if (power_battery_flags_hold & BatteryFlag.OVERCURRENT):
                periphery.write_pixel(83, 38)
            if (power_battery_flags_hold & BatteryFlag.UNDERCURRENT):
                periphery.write_pixel(83, 45)

            if power_battery_discharge_status:
                periphery.set_size(5, 8)
                periphery.draw_word('[-+]!', 64, 6)

            periphery.display()
