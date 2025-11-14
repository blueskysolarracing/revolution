from dataclasses import dataclass, field
from enum import auto, Enum
from functools import reduce
from logging import getLogger
from operator import or_
from queue import Queue
from statistics import mean
from typing import Any

from adafruit_gps import GPS  # type: ignore[import-untyped]
from battlib import Battery
from can import BusABC
from door.threading2 import AcquirableDoor
from iclib.adc78h89 import ADC78H89, InputChannel
from iclib.bno055 import BNO055
from iclib.ina229 import INA229
from iclib.lis2ds12 import LIS2DS12
from iclib.tmag5273 import TMAG5273
from iclib.wavesculptor22 import WaveSculptor22
from periphery import GPIO, PWM
from serial import Serial

from revolution.battery_management_system import (
    BatteryFlag,
    BatteryManagementSystem,
)
from revolution.LIS2HH12 import LIS2HH12
from revolution.steering_wheel import SteeringWheel
from revolution.utilities import Direction, PRBS

_logger = getLogger(__name__)


class Endpoint(Enum):
    DEBUGGER = auto()
    DISPLAY = auto()
    DRIVER = auto()
    MISCELLANEOUS = auto()
    MOTOR = auto()
    POWER = auto()
    TELEMETRY = auto()


class Header(Enum):
    STOP = auto()
    CAN = auto()


@dataclass(frozen=True)
class Message:
    header: Header
    args: tuple[Any, ...] = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class Contexts:
    # General

    general_unused_status_input: bool

    # Debugger

    # Display

    # Driver

    # Miscellaneous

    miscellaneous_left_indicator_light_status_input: bool
    miscellaneous_right_indicator_light_status_input: bool
    miscellaneous_hazard_lights_status_input: bool
    miscellaneous_daytime_running_lights_status_input: bool
    miscellaneous_horn_status_input: bool
    miscellaneous_backup_camera_control_status_input: bool
    miscellaneous_brake_status_input: bool
    miscellaneous_orientation: dict[str, float]
    miscellaneous_latitude: float
    miscellaneous_longitude: float

    miscellaneous_left_wheel_velocity: float
    miscellaneous_left_wheel_magnetic_field: float
    miscellaneous_right_wheel_velocity: float
    miscellaneous_right_wheel_magnetic_field: float
    miscellaneous_left_wheel_accelerations: list[float]
    miscellaneous_right_wheel_accelerations: list[float]

    # Motor

    motor_status_input: bool
    motor_acceleration_input: float
    motor_direction_input: Direction
    motor_cruise_control_status_input: bool
    motor_cruise_control_velocity: float
    motor_regeneration_status_input: bool
    motor_variable_field_magnet_up_input: int
    motor_variable_field_magnet_down_input: int
    motor_variable_field_magnet_position: int
    motor_velocity: float
    motor_heartbeat_timestamp: float

    motor_controller_sent_values: list[float]
    motor_controller_limit_flags: int
    motor_controller_error_flags: int
    motor_controller_active_motor: int
    motor_controller_transmit_error_count: int
    motor_controller_receive_error_count: int
    motor_controller_bus_voltage: float
    motor_controller_bus_current: float
    motor_controller_vehicle_velocity: float
    motor_controller_phase_B_current: float
    motor_controller_phase_C_current: float
    motor_controller_Vq: float
    motor_controller_Vd: float
    motor_controller_Iq: float
    motor_controller_Id: float
    motor_controller_BEMFq: float
    motor_controller_BEMFd: float
    motor_controller_supply_15v: float
    motor_controller_supply_1_9v: float
    motor_controller_supply_3_3v: float
    motor_controller_motor_temp: float
    motor_controller_heat_sink_temp: float
    motor_controller_dsp_board_temp: float
    motor_controller_odometer: float
    motor_controller_dc_bus_amphours: float
    motor_controller_slip_speed: float

    # Power

    power_array_relay_status_input: bool
    power_battery_relay_status_input: bool
    power_battery_cell_voltages: list[float]
    power_battery_thermistor_temperatures: list[float]
    power_battery_HV_bus_voltage: float
    power_battery_HV_current: float
    power_battery_LV_bus_voltage: float
    power_battery_LV_current: float
    power_battery_supp_voltage: float

    power_battery_relay_status: bool
    power_battery_electric_safe_discharge_status: bool
    power_battery_discharge_status: bool
    power_battery_cell_flags: list[int]
    power_battery_thermistor_flags: list[int]
    power_battery_current_flag: int
    power_battery_flags_hold: int
    power_battery_heartbeat_timestamp: float
    power_battery_state_of_charges: list[float]

    power_psm_battery_current: float
    power_psm_battery_voltage: float
    power_psm_array_current: float
    power_psm_array_voltage: float
    power_psm_motor_current: float
    power_psm_motor_voltage: float

    @property
    def power_battery_min_cell_voltage(self) -> float:
        return min(self.power_battery_cell_voltages)

    @property
    def power_battery_max_cell_voltage(self) -> float:
        return max(self.power_battery_cell_voltages)

    @property
    def power_battery_mean_cell_voltage(self) -> float:
        return mean(self.power_battery_cell_voltages)

    @property
    def power_battery_min_thermistor_temperature(self) -> float:
        return min(self.power_battery_thermistor_temperatures)

    @property
    def power_battery_max_thermistor_temperature(self) -> float:
        return max(self.power_battery_thermistor_temperatures)

    @property
    def power_battery_mean_thermistor_temperature(self) -> float:
        return mean(self.power_battery_thermistor_temperatures)

    @property
    def power_battery_min_state_of_charge(self) -> float:
        return min(self.power_battery_state_of_charges)

    @property
    def power_battery_max_state_of_charge(self) -> float:
        return max(self.power_battery_state_of_charges)

    @property
    def power_battery_mean_state_of_charge(self) -> float:
        return mean(self.power_battery_state_of_charges)

    @property
    def power_battery_flags(self) -> BatteryFlag:
        return (
            reduce(  # type: ignore[return-value]
                or_,
                self.power_battery_cell_flags,
            )
            | reduce(or_, self.power_battery_thermistor_flags)
            | self.power_battery_current_flag
        )

    # Telemetry


@dataclass(frozen=True)
class Peripheries:
    # General

    general_can_bus: BusABC

    # Debugger

    # Display

    # Driver

    driver_steering_wheel: SteeringWheel

    driver_pedals_adc78h89: ADC78H89

    driver_general_unused_switch_prbs: PRBS

    driver_miscellaneous_left_indicator_light_switch_prbs: PRBS
    driver_miscellaneous_right_indicator_light_switch_prbs: PRBS
    driver_miscellaneous_hazard_lights_switch_prbs: PRBS
    driver_miscellaneous_daytime_running_lights_switch_prbs: PRBS
    driver_miscellaneous_horn_switch_prbs: PRBS
    driver_miscellaneous_backup_camera_control_switch_prbs: PRBS
    driver_miscellaneous_brake_switch_gpio: GPIO

    driver_motor_cruise_control_velocity_rotary_encoder_a_prbs: PRBS
    driver_motor_cruise_control_velocity_rotary_encoder_b_prbs: PRBS
    driver_motor_direction_switch_prbs: PRBS
    driver_motor_regeneration_switch_prbs: PRBS
    driver_motor_variable_field_magnet_up_switch_prbs: PRBS
    driver_motor_variable_field_magnet_down_switch_prbs: PRBS
    driver_motor_cruise_control_switch_prbs: PRBS
    driver_motor_acceleration_input_input_channel: InputChannel

    driver_power_array_relay_switch_prbs: PRBS
    driver_power_battery_relay_switch_prbs: PRBS

    # Miscellaneous

    miscellaneous_left_indicator_light_pwm: PWM
    miscellaneous_right_indicator_light_pwm: PWM
    miscellaneous_daytime_running_lights_pwm: PWM
    miscellaneous_brake_lights_pwm: PWM
    miscellaneous_backup_camera_control_switch_gpio: GPIO
    miscellaneous_orientation_imu_bno055: BNO055
    miscellaneous_position_gps: GPS
    miscellaneous_left_wheel_hall_effect: TMAG5273
    miscellaneous_right_wheel_hall_effect: TMAG5273
    miscellaneous_left_wheel_accelerometer: LIS2HH12
    miscellaneous_right_wheel_accelerometer: LIS2HH12

    # Motor

    motor_wavesculptor22: WaveSculptor22

    motor_variable_field_magnet_direction_gpio: GPIO
    motor_variable_field_magnet_stall_gpio: GPIO
    motor_variable_field_magnet_encoder_a_gpio: GPIO
    motor_variable_field_magnet_encoder_b_gpio: GPIO
    motor_variable_field_magnet_enable_gpio: GPIO

    # Power

    power_array_relay_low_side_gpio: GPIO
    power_array_relay_high_side_gpio: GPIO
    power_array_relay_pre_charge_gpio: GPIO
    power_point_tracking_switch_1_gpio: GPIO
    power_point_tracking_switch_2_gpio: GPIO
    power_battery_management_system: BatteryManagementSystem
    power_psm_motor_ina229: INA229
    power_psm_battery_ina229: INA229
    power_psm_array_ina229: INA229

    # Telemetry

    telemetry_radio_serial: Serial


@dataclass(frozen=True)
class Settings:
    # General

    general_wheel_diameter: float
    general_log_filepath: str

    # Debugger

    # Display

    display_frame_rate: float
    """The display frame rate (in frames/second)."""
    display_font_pathname: str
    """The display font pathname (.ttf file)."""

    # Driver

    driver_timeout: float

    # Miscellaneous

    miscellaneous_light_timeout: float
    miscellaneous_light_flash_timeout: float
    miscellaneous_orientation_timeout: float
    miscellaneous_position_timeout: float
    miscellaneous_front_wheels_timeout: float

    # Motor

    motor_control_timeout: float
    motor_variable_field_magnet_timeout: float

    motor_acceleration_input_max_increase: float
    motor_acceleration_input_max_decrease: float
    motor_filtered_acceleration_input_factor: float
    motor_bus_current_limit: float
    motor_regeneration_strength: float
    motor_variable_field_magnet_step_size: int
    motor_variable_field_magnet_step_upper_limit: int
    motor_variable_field_magnet_frequency: int
    motor_variable_field_magnet_duty_cycle: float
    motor_variable_field_magnet_stall_threshold: int
    motor_variable_field_magnet_max_enable_time_reset: float
    motor_variable_field_magnet_max_enable_time_move: float

    # Power

    power_monitor_timeout: float
    power_array_relay_timeout: float
    power_point_tracking_timeout: float
    power_soc_timeout: float
    power_psm_timeout: float
    power_steering_wheel_led_timeout: float
    power_battery: Battery
    power_disable_charging_battery_soc_threshold: float
    power_psm_motor_ina229_voltage_correction_factor: float
    power_psm_battery_ina229_voltage_correction_factor: float
    power_psm_array_ina229_voltage_correction_factor: float
    power_battery_overcurrent_limit: float
    power_battery_undercurrent_limit: float
    power_log_timeout: float

    # Telemetry

    telemetry_timeout: float
    telemetry_begin_token: bytes
    telemetry_separator_token: bytes
    telemetry_end_token: bytes


@dataclass(frozen=True)
class Environment:
    contexts: AcquirableDoor[Contexts]
    peripheries: Peripheries
    settings: Settings
    __queues: dict[Endpoint, Queue[Message]] = field(
        default_factory=dict,
        init=False,
    )

    def __post_init__(self) -> None:
        for endpoint in Endpoint:
            self.__queues[endpoint] = Queue()

    def receive(
            self,
            endpoint: Endpoint,
            block: bool = True,
            timeout: float | None = None,
    ) -> Message:
        return self.__queues[endpoint].get(block, timeout)

    def send(
            self,
            endpoint: Endpoint,
            message: Message,
            block: bool = True,
            timeout: float | None = None,
    ) -> None:
        self.__queues[endpoint].put(message, block, timeout)

    def send_all(
            self,
            message: Message,
            block: bool = True,
            timeout: float | None = None,
    ) -> None:
        for queue in self.__queues.values():
            queue.put(message, block, timeout)

    def stop(self, block: bool = True, timeout: float | None = None) -> None:
        self.send_all(Message(Header.STOP))
