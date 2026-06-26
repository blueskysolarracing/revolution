from dataclasses import dataclass
from logging import getLogger
from typing import ClassVar

from revolution.application import Application
from revolution.battery_management_system import BatteryFlag
from revolution.environment import Endpoint
from revolution.steering_wheel import DisplayItem
from revolution.utilities import Direction
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
        periphery.clear_screen()

        def config_display() -> None:
            # Motor
            periphery.set_text_position(DisplayItem.VELOCITY_HEADER, 325, 1)
            periphery.set_text_size(DisplayItem.VELOCITY_HEADER, 4)
            periphery.draw_word(DisplayItem.VELOCITY_HEADER, 'SPEED KM/H')

            periphery.set_text_position(DisplayItem.VELOCITY, 340, 5)
            periphery.set_text_size(DisplayItem.VELOCITY, 13)

            periphery.set_text_position(DisplayItem.REVERSE, 487, 17)
            periphery.set_text_size(DisplayItem.REVERSE, 8)

            periphery.set_text_position(DisplayItem.CRUISE_HEADER, 310, 28)
            periphery.set_text_size(DisplayItem.CRUISE_HEADER, 4)
            periphery.draw_word(DisplayItem.CRUISE_HEADER, 'CRUISE')

            periphery.set_text_position(DisplayItem.CRUISE_VELOCITY, 310, 33)
            periphery.set_text_size(DisplayItem.CRUISE_VELOCITY, 8)

            periphery.set_text_position(DisplayItem.REGEN, 437, 17)
            periphery.set_text_size(DisplayItem.REGEN, 8)

            periphery.set_text_position(DisplayItem.MOTOR_STATUS, 387, 17)
            periphery.set_text_size(DisplayItem.MOTOR_STATUS, 8)
            periphery.set_text_mode(DisplayItem.MOTOR_STATUS, 4)

            periphery.set_text_position(DisplayItem.VFM_HEADER, 459, 28)
            periphery.set_text_size(DisplayItem.VFM_HEADER, 4)
            periphery.draw_word(DisplayItem.VFM_HEADER, 'VFM')

            periphery.set_text_position(DisplayItem.VFM_GEAR, 447, 33)
            periphery.set_text_size(DisplayItem.VFM_GEAR, 8)

            # Battery
            periphery.set_text_position(DisplayItem.BAT_SOC_HEADER, 15, 1)
            periphery.set_text_size(DisplayItem.BAT_SOC_HEADER, 4)
            periphery.draw_word(DisplayItem.BAT_SOC_HEADER, 'BATT SOC %')

            periphery.set_text_position(DisplayItem.BAT_SOC, 30, 5)
            periphery.set_text_size(DisplayItem.BAT_SOC, 13)

            periphery.set_text_position(DisplayItem.SAFE_STATE, 15, 17)
            periphery.set_text_size(DisplayItem.SAFE_STATE, 8)
            periphery.set_text_mode(DisplayItem.SAFE_STATE, 2)

            periphery.set_text_position(DisplayItem.BMS_VOLT, 15, 25)
            periphery.set_text_size(DisplayItem.BMS_VOLT, 5)

            periphery.set_text_position(DisplayItem.BMS_TEMP, 15, 30)
            periphery.set_text_size(DisplayItem.BMS_TEMP, 5)

            periphery.set_text_position(DisplayItem.BMS_CURRENT, 15, 35)
            periphery.set_text_size(DisplayItem.BMS_CURRENT, 5)

            # Battery Flags
            periphery.set_text_position(DisplayItem.BMS_VOLT_FLAG, 252, 26)
            periphery.set_text_size(DisplayItem.BMS_VOLT_FLAG, 4)
            periphery.set_text_mode(DisplayItem.BMS_VOLT_FLAG, 4)

            periphery.set_text_position(DisplayItem.BMS_TEMP_FLAG, 252, 31)
            periphery.set_text_size(DisplayItem.BMS_TEMP_FLAG, 4)
            periphery.set_text_mode(DisplayItem.BMS_TEMP_FLAG, 4)

            periphery.set_text_position(DisplayItem.BMS_CURRENT_FLAG, 252, 36)
            periphery.set_text_size(DisplayItem.BMS_CURRENT_FLAG, 4)
            periphery.set_text_mode(DisplayItem.BMS_CURRENT_FLAG, 4)
            periphery.set_text_mode(DisplayItem.BMS_CURRENT_FLAG, 4)

            # Relays
            periphery.set_text_position(DisplayItem.ARRAY_RELAY, 287, 17)
            periphery.set_text_size(DisplayItem.ARRAY_RELAY, 8)
            periphery.set_text_mode(DisplayItem.ARRAY_RELAY, 0)

            periphery.set_text_position(DisplayItem.BATTERY_RELAY, 337, 17)
            periphery.set_text_size(DisplayItem.BATTERY_RELAY, 8)

        timeout = 1 / self.environment.settings.display_frame_rate

        config_period = self.environment.settings.display_frame_rate
        display_counter = 0

        while not self._stoppage.wait(timeout):
            if (display_counter % config_period == 0):
                config_display()

            with self.environment.contexts() as contexts:
                # Motor
                motor_velocity = contexts.motor_velocity
                motor_direction_input = contexts.motor_direction_input
                motor_cruise_control_status_input = (
                    contexts.motor_cruise_control_status_input
                )
                motor_cruise_control_velocity = (
                    contexts.motor_cruise_control_velocity
                )
                motor_regeneration_status_input = (
                    contexts.motor_regeneration_status_input
                )
                motor_heartbeat_working = contexts.motor_heartbeat_working
                motor_controller_error_flags = (
                    contexts.motor_controller_error_flags
                )
                motor_variable_field_magnet_position = (
                    contexts.motor_variable_field_magnet_position
                )

                # Battery
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
                power_battery_min_thermistor_temperature = (
                    contexts.power_battery_min_thermistor_temperature
                )
                power_battery_max_thermistor_temperature = (
                    contexts.power_battery_max_thermistor_temperature
                )
                power_battery_HV_current = (
                    contexts.power_battery_HV_current
                )

                # Battery Flags
                power_battery_flags_hold = (
                    contexts.power_battery_flags_hold
                )

                # Relays
                power_array_relay_status = contexts.power_array_relay_status
                power_battery_relay_status = (
                    contexts.power_battery_relay_status
                )

            # Motor

            motor_velocity = clip_value(motor_velocity, -99, 180)
            periphery.draw_word(DisplayItem.VELOCITY, f'{motor_velocity:3.0f}')

            reverse_label = (
                'R' if motor_direction_input == Direction.BACKWARD else ''
            )
            periphery.draw_word(DisplayItem.REVERSE, reverse_label)

            if motor_cruise_control_status_input:
                cruise_velocity = clip_value(
                    motor_cruise_control_velocity, -99, 180
                )
                cruise_label = f'{cruise_velocity:3.0f}'
            else:
                cruise_label = 'OFF'
            periphery.draw_word(DisplayItem.CRUISE_VELOCITY, cruise_label)

            regen_label = 'G' if motor_regeneration_status_input else ''
            periphery.draw_word(DisplayItem.REGEN, regen_label)

            motor_fault = (
                not motor_heartbeat_working or motor_controller_error_flags
            )
            motor_status_label = 'M' if motor_fault else ''
            periphery.draw_word(DisplayItem.MOTOR_STATUS, motor_status_label)

            motor_variable_field_magnet_step = (
                motor_variable_field_magnet_position
                // (
                    self
                    .environment
                    .settings
                    .motor_variable_field_magnet_step_size
                )
            )
            vfm_step = clip_value(motor_variable_field_magnet_step, -1, 99)
            periphery.draw_word(DisplayItem.VFM_GEAR, f'{vfm_step:2.0f}')

            # Battery

            power_battery_state_of_charge = clip_value(
                power_battery_state_of_charge, -0.01, 1.01
            )
            periphery.draw_word(
                DisplayItem.BAT_SOC,
                f'{power_battery_state_of_charge * 100:3.0f}',
            )

            safe_state_label = (
                'FAULT' if power_battery_discharge_status else ''
            )
            periphery.draw_word(DisplayItem.SAFE_STATE, safe_state_label)

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
                power_battery_min_thermistor_temperature, -1, 99
            )
            power_battery_max_thermistor_temperature = clip_value(
                power_battery_max_thermistor_temperature, -1, 99
            )
            periphery.draw_word(
                DisplayItem.BMS_TEMP,
                f'T {power_battery_min_thermistor_temperature:3.0f}'
                f' {power_battery_max_thermistor_temperature:3.0f}',
            )

            power_battery_HV_current = clip_value(
                power_battery_HV_current, -100, 100
            )
            periphery.draw_word(
                DisplayItem.BMS_CURRENT,
                f'I {power_battery_HV_current:7.2f}',
            )

            # Battery Flags

            if power_battery_flags_hold & BatteryFlag.OVERVOLTAGE:
                ov_label = 'O'
            else:
                ov_label = ' '
            if power_battery_flags_hold & BatteryFlag.UNDERVOLTAGE:
                uv_label = 'U'
            else:
                uv_label = ' '
            periphery.draw_word(
                DisplayItem.BMS_VOLT_FLAG, f'{ov_label}{uv_label}'
            )

            if power_battery_flags_hold & BatteryFlag.OVERTEMPERATURE:
                ot_label = 'O'
            else:
                ot_label = ' '
            if power_battery_flags_hold & BatteryFlag.UNDERTEMPERATURE:
                ut_label = 'U'
            else:
                ut_label = ' '
            periphery.draw_word(
                DisplayItem.BMS_TEMP_FLAG, f'{ot_label}{ut_label}'
            )

            if power_battery_flags_hold & BatteryFlag.OVERCURRENT:
                oc_label = 'O'
            else:
                oc_label = ''
            if power_battery_flags_hold & BatteryFlag.UNDERCURRENT:
                uc_label = 'U'
            else:
                uc_label = ''
            periphery.draw_word(
                DisplayItem.BMS_CURRENT_FLAG, f'{oc_label}{uc_label}'
            )

            # Relays
            array_relay_label = 'A' if power_array_relay_status else ''
            periphery.draw_word(DisplayItem.ARRAY_RELAY, array_relay_label)

            battery_relay_label = 'B' if power_battery_relay_status else ''
            periphery.draw_word(DisplayItem.BATTERY_RELAY, battery_relay_label)

            display_counter += 1
