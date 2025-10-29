from dataclasses import dataclass
from logging import getLogger
from typing import ClassVar

from revolution.application import Application
from revolution.battery_management_system import BatteryFlag
from revolution.environment import Endpoint
from revolution.steering_wheel import DisplayItem
from revolution.worker import Worker

_logger = getLogger(__name__)


@dataclass
class Display(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.DISPLAY

    def _setup(self) -> None:
        super()._setup()

        self._display_worker = Worker(target=self._display)

        self._display_worker.start()

    def _teardown(self) -> None:
        self._display_worker.join()

    def _display(self) -> None:

        def clip_value(value: float, min_: float, max_: float) -> float:
            if value > max_:
                return max_
            elif value < min_:
                return min_
            else:
                return value

        periphery = self.environment.peripheries.driver_steering_wheel
        # periphery.clear_screen()

        # periphery.set_text_position(DisplayItem.BAT_HEADER, 15, 1)
        # periphery.set_text_size(DisplayItem.BAT_HEADER, 4)
        # periphery.draw_word(DisplayItem.BAT_HEADER, 'BATTERIES')

        # periphery.set_text_position(DisplayItem.VEL_HEADER, 390, 1)
        # periphery.set_text_size(DisplayItem.VEL_HEADER, 4)
        # periphery.draw_word(DisplayItem.VEL_HEADER, 'DRIVER')

        periphery.set_text_position(DisplayItem.BAT_SOC, 15, 5)
        periphery.set_text_size(DisplayItem.BAT_SOC, 13)

        periphery.set_text_position(DisplayItem.BAT_SOC_UNIT, 15, 1)
        periphery.set_text_size(DisplayItem.BAT_SOC_UNIT, 4)
        periphery.draw_word(DisplayItem.BAT_SOC_UNIT, 'BATT SOC %')

        periphery.set_text_position(DisplayItem.VELOCITY, 330, 5)
        periphery.set_text_size(DisplayItem.VELOCITY, 13)

        periphery.set_text_position(DisplayItem.VELOCITY_UNIT, 315, 1)
        periphery.set_text_size(DisplayItem.VELOCITY_UNIT, 4)
        periphery.draw_word(DisplayItem.VELOCITY_UNIT, 'SPEED KM/H')

        periphery.set_text_position(DisplayItem.REGEN, 322, 17)
        periphery.set_text_size(DisplayItem.REGEN, 8)
        periphery.set_text_mode(DisplayItem.REGEN, 2)

        periphery.set_text_position(DisplayItem.SAFE_STATE, 15, 17)
        periphery.set_text_size(DisplayItem.SAFE_STATE, 8)
        periphery.set_text_mode(DisplayItem.SAFE_STATE, 2)

        periphery.set_text_position(DisplayItem.CRUISE_CTRL, 300, 25)
        periphery.set_text_size(DisplayItem.CRUISE_CTRL, 4)
        periphery.draw_word(DisplayItem.CRUISE_CTRL, 'CRUISE')
        
        periphery.set_text_position(DisplayItem.CRUISE_CTRL_VEL, 300, 30)
        periphery.set_text_size(DisplayItem.CRUISE_CTRL_VEL, 8)

        periphery.set_text_position(DisplayItem.VFM, 435, 25)
        periphery.set_text_size(DisplayItem.VFM, 4)
        periphery.draw_word(DisplayItem.VFM, 'GEAR')

        periphery.set_text_position(DisplayItem.VFM_GEAR, 456, 30)
        periphery.set_text_size(DisplayItem.VFM_GEAR, 8)

        periphery.set_text_position(DisplayItem.BMS_VOLT, 15, 25)
        periphery.set_text_size(DisplayItem.BMS_VOLT, 5)

        periphery.set_text_position(DisplayItem.BMS_TEMP, 15, 30)
        periphery.set_text_size(DisplayItem.BMS_TEMP, 5)

        periphery.set_text_position(DisplayItem.BMS_CURRENT, 15, 35)
        periphery.set_text_size(DisplayItem.BMS_CURRENT, 5)

        timeout = 1 / self.environment.settings.display_frame_rate

        while not self._stoppage.wait(timeout):
            with self.environment.contexts() as contexts:
                motor_velocity = contexts.motor_velocity
                motor_cruise_control_status_input = (
                    contexts.motor_cruise_control_status_input
                )
                motor_cruise_control_velocity = (
                    contexts.motor_cruise_control_velocity
                )
                motor_regeneration_status_input = (
                    contexts.motor_regeneration_status_input
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
                power_battery_HV_current = (
                    contexts.power_battery_HV_current
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

            # Motor

            if motor_regeneration_status_input:
                periphery.draw_word(DisplayItem.REGEN, 'REGEN')
            else:
                periphery.draw_word(DisplayItem.REGEN, '')
            
            motor_velocity = clip_value(motor_velocity, -99, 180)
            periphery.draw_word(DisplayItem.VELOCITY, f'{motor_velocity:3.0f}')

            motor_cruise_control_label = (
                'ON' if motor_cruise_control_status_input else 'OFF'
            )

            if motor_cruise_control_status_input:
                periphery.draw_word(
                    DisplayItem.CRUISE_CTRL_VEL,
                    (f'{motor_cruise_control_velocity:.0f}'),
                )
            else:
                periphery.draw_word(DisplayItem.CRUISE_CTRL_VEL, "OFF")

            motor_variable_field_magnet_step = (
                motor_variable_field_magnet_position / 32
            )

            periphery.draw_word(
                DisplayItem.VFM_GEAR,
                (f'{motor_variable_field_magnet_step:1.0f}'),
            )

            # Power

            power_battery_state_of_charge = clip_value(
                power_battery_state_of_charge, -0.01, 1.01
            )
            periphery.draw_word(
                DisplayItem.BAT_SOC,
                f'{power_battery_state_of_charge * 100:3.0f}',
            )

            power_battery_min_cell_voltage = clip_value(
                power_battery_min_cell_voltage, 0.0, 9.9
            )
            power_battery_max_cell_voltage = clip_value(
                power_battery_max_cell_voltage, 0.0, 9.9
            )
            periphery.draw_word(
                DisplayItem.BMS_VOLT,
                (
                    f'V {power_battery_min_cell_voltage:3.1f}'
                    f' {power_battery_max_cell_voltage:3.1f}'
                ),
            )

            power_battery_min_thermistor_temperature = clip_value(
                power_battery_min_thermistor_temperature, 0, 99
            )
            power_battery_max_thermistor_temperature = clip_value(
                power_battery_max_thermistor_temperature, 0, 99
            )
            periphery.draw_word(
                DisplayItem.BMS_TEMP,
                f'T {power_battery_min_thermistor_temperature:2.0f}'
                f'  {power_battery_max_thermistor_temperature:2.0f}',
            )

            power_battery_HV_current = clip_value(
                power_battery_HV_current, -50, 99
            )
            periphery.draw_word(
                DisplayItem.BMS_CURRENT,
                f'I {power_battery_HV_current:6.2f}',
            )

            # if (power_battery_flags_hold & BatteryFlag.OVERVOLTAGE):
            #     periphery.write_pixel(83, 18)
            # if (power_battery_flags_hold & BatteryFlag.UNDERVOLTAGE):
            #     periphery.write_pixel(83, 25)
            # if (power_battery_flags_hold & BatteryFlag.OVERTEMPERATURE):
            #     periphery.write_pixel(83, 28)
            # if (power_battery_flags_hold & BatteryFlag.UNDERTEMPERATURE):
            #     periphery.write_pixel(83, 35)
            # if (power_battery_flags_hold & BatteryFlag.OVERCURRENT):
            #     periphery.write_pixel(83, 38)
            # if (power_battery_flags_hold & BatteryFlag.UNDERCURRENT):
            #     periphery.write_pixel(83, 45)

            if power_battery_discharge_status:
                periphery.draw_word(DisplayItem.SAFE_STATE, 'FAULT')
            else:
                periphery.draw_word(DisplayItem.SAFE_STATE, '')
