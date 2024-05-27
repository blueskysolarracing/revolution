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

        periphery = self.environment.peripheries.nhd_c12864a1z_fsw_fbw_htt

        periphery.configure()
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
                battery_soc = 0.5
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

            periphery = self.environment.peripheries.nhd_c12864a1z_fsw_fbw_htt

            periphery.clear_screen()

            # draw here!

            # Display motor speed (km/h)
            
            motor_speed = (motor_speed * 3600) / 1000
            periphery.set_size(22, 24)
            if (motor_speed >= 100):
                periphery.draw_word(str(motor_speed), 30, 26)
            else:
                periphery.draw_word(str(motor_speed), 52, 26)
                
            periphery.set_size(16, 20)
            periphery.draw_word('km/h', 100, 36)
            
            # Display indicator status
            
            periphery.set_size(10, 12)
            
            if (left_indicator_light_status):
                periphery.draw_word('<', 5, 5)
            if (right_indicator_light_status):
                periphery.draw_word('>', 18, 5)
            if (hazard_lights_status):
                periphery.set_size(6, 12)
                periphery.draw_word('(', 31, 5)
                periphery.set_size(10, 12)
                periphery.draw_word('!!', 38, 5)
                periphery.set_size(6, 12)
                periphery.draw_word(')', 59, 5)
                
            # Display SOC
            
            formatted_soc = f'{battery_soc * 100:.1f}%'
            periphery.set_size(10, 12)
            periphery.draw_word(formatted_soc, 82, 5)
            
            # Display battery warning
            
            periphery.set_size(6, 6)
            if (battery_warning_status):
                periphery.draw_word('[-+]!', 5, 56)
                
            # Display motor target speed
            
            periphery.set_size(8, 10)
            periphery.draw_word('Target: ', 30, 52)
            motor_target_speed = (motor_target_speed * 3600) / 1000
            periphery.draw_word(str(motor_target_speed), 30, 52)
            
            # Consult: https://github.com/blueskysolarracing/iclib
            # motor speed is in m/s. convert to km/h
            # f'{battery_soc * 100:.1f}%'
            #periphery.draw_word(battery_soc, 2, 2)

            periphery.display()
