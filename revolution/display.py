from dataclasses import dataclass
from logging import getLogger
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
                motor_speed = contexts.motor_speed
                power_state_of_charge = contexts.power_state_of_charge
                hazard_lights_status = (
                    contexts.miscellaneous_hazard_lights_status_input
                )
                left_indicator_light_status = (
                    contexts.miscellaneous_left_indicator_light_status_input
                )
                right_indicator_light_status = (
                    contexts.miscellaneous_right_indicator_light_status_input
                )
                battery_warning_status = False
                motor_target_speed = None

            periphery = (
                self.environment.peripheries.display_nhd_c12864a1z_fsw_fbw_htt
            )

            periphery.clear_screen()

            # Motor speed

            motor_speed = (motor_speed * 3600) / 1000

            periphery.set_size(22, 24)
            periphery.draw_word(f'{motor_speed:3.0f}', 52, 26)
            periphery.set_size(16, 20)
            periphery.draw_word('km/h', 100, 36)

            # Indicator status

            if left_indicator_light_status:
                periphery.set_size(10, 12)
                periphery.draw_word('<', 5, 5)

            if right_indicator_light_status:
                periphery.set_size(10, 12)
                periphery.draw_word('>', 18, 5)

            if hazard_lights_status:
                periphery.set_size(6, 12)
                periphery.draw_word('(', 31, 5)
                periphery.set_size(10, 12)
                periphery.draw_word('!!', 38, 5)
                periphery.set_size(6, 12)
                periphery.draw_word(')', 59, 5)

            # SOC

            periphery.set_size(10, 12)
            periphery.draw_word(f'{power_state_of_charge * 100:.0f}%', 82, 5)

            # Battery warning

            if battery_warning_status:
                periphery.set_size(6, 6)
                periphery.draw_word('[-+]!', 5, 56)

            # Motor target speed

            if motor_target_speed is not None:
                motor_target_speed = (motor_target_speed * 3600) / 1000

                periphery.set_size(8, 10)
                periphery.draw_word(
                    f'Target: {motor_target_speed:3.0f}',
                    30,
                    52,
                )

            periphery.display()
