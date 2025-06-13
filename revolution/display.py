from dataclasses import dataclass
from logging import getLogger
from statistics import mean
from typing import ClassVar

from revolution.application import Application
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
                power_battery_state_of_charges = (
                    contexts.power_battery_state_of_charges.copy()
                )
                power_battery_discharge_status = (
                    contexts.power_battery_discharge_status
                )

            periphery = (
                self.environment.peripheries.display_nhd_c12864a1z_fsw_fbw_htt
            )

            periphery.clear_screen()

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
            periphery.draw_word('km/h', 78, 27)

            motor_cruise_control_label = (
                'ON' if motor_cruise_control_status_input else 'OFF'
            )

            periphery.set_size(6, 12)
            periphery.draw_word(
                (
                    f'CC ({motor_cruise_control_label}):'
                    f' {motor_cruise_control_velocity:3.0f} '
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

            power_battery_state_of_charge = mean(
                power_battery_state_of_charges,
            )

            periphery.set_size(8, 12)
            periphery.draw_word(
                f'{power_battery_state_of_charge * 100:.0f}%',
                93,
                4,
            )

            if power_battery_discharge_status:
                periphery.set_size(5, 8)
                periphery.draw_word('[-+]!', 64, 6)

            periphery.display()
