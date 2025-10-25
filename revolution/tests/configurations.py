from collections import defaultdict
from dataclasses import make_dataclass
from math import inf
from unittest.mock import MagicMock

from adafruit_gps import GPS  # type: ignore[import-untyped]
from battlib import Battery
from can import BusABC
from iclib.adc78h89 import ADC78H89, InputChannel
from iclib.bno055 import BNO055
from iclib.ina229 import INA229
from iclib.lis2ds12 import LIS2DS12
from iclib.tmag5273 import TMAG5273
from iclib.wavesculptor22 import WaveSculptor22
from json import load
from periphery import GPIO, PWM
from serial import Serial

from revolution import (
    Application,
    BATTERY_CELL_COUNT,
    BatteryManagementSystem,
    BATTERY_THERMISTOR_COUNT,
    Contexts,
    Debugger,
    Direction,
    Display,
    Driver,
    LIS2HH12,
    Miscellaneous,
    Motor,
    Peripheries,
    Power,
    PRBS,
    Settings,
    SteeringWheel,
    Telemetry,
)

APPLICATION_TYPES: tuple[type[Application], ...] = (
    Debugger,
    Display,
    Driver,
    Miscellaneous,
    Motor,
    Power,
    Telemetry,
)

CONTEXTS: Contexts = Contexts(
    # General

    general_unused_status_input=False,

    # Debugger

    # Display

    # Driver

    # Miscellaneous

    miscellaneous_left_indicator_light_status_input=False,
    miscellaneous_right_indicator_light_status_input=False,
    miscellaneous_hazard_lights_status_input=False,
    miscellaneous_daytime_running_lights_status_input=False,
    miscellaneous_horn_status_input=False,
    miscellaneous_backup_camera_control_status_input=False,
    miscellaneous_brake_status_input=False,
    miscellaneous_orientation={},
    miscellaneous_latitude=0,
    miscellaneous_longitude=0,

    miscellaneous_left_wheel_velocity=0,
    miscellaneous_left_wheel_magnetic_field=0,
    miscellaneous_right_wheel_velocity=0,
    miscellaneous_right_wheel_magnetic_field=0,
    miscellaneous_left_wheel_accelerations=[0, 0, 0],
    miscellaneous_right_wheel_accelerations=[0, 0, 0],

    # Motor

    motor_status_input=False,
    motor_acceleration_input=0,
    motor_direction_input=Direction.FORWARD,
    motor_cruise_control_status_input=False,
    motor_cruise_control_velocity=0,
    motor_regeneration_status_input=False,
    motor_variable_field_magnet_up_input=0,
    motor_variable_field_magnet_down_input=0,
    motor_variable_field_magnet_position=0,
    motor_velocity=0,
    motor_heartbeat_timestamp=inf,

    motor_controller_limit_flags=0,
    motor_controller_error_flags=0,
    motor_controller_active_motor=0,
    motor_controller_transmit_error_count=0,
    motor_controller_receive_error_count=0,

    motor_controller_15V_rail_voltage=0,

    # Power

    power_array_relay_status_input=False,
    power_battery_relay_status_input=False,
    power_battery_cell_voltages=[0 for _ in range(BATTERY_CELL_COUNT)],
    power_battery_thermistor_temperatures=[
        0 for _ in range(BATTERY_THERMISTOR_COUNT)
    ],
    power_battery_HV_bus_voltage=0,
    power_battery_HV_current=0,
    power_battery_LV_bus_voltage=0,
    power_battery_LV_current=0,
    power_battery_supp_voltage=0,

    power_battery_relay_status=False,
    power_battery_electric_safe_discharge_status=False,
    power_battery_discharge_status=False,
    power_battery_cell_flags=[0 for _ in range(BATTERY_CELL_COUNT)],
    power_battery_thermistor_flags=[
        0 for _ in range(BATTERY_THERMISTOR_COUNT)
    ],
    power_battery_current_flag=0,
    power_battery_flags_hold=0,
    power_battery_heartbeat_timestamp=inf,
    power_battery_state_of_charges=[0 for _ in range(BATTERY_CELL_COUNT)],

    power_psm_motor_current=0,
    power_psm_motor_voltage=0,
    power_psm_battery_current=0,
    power_psm_battery_voltage=0,
    power_psm_array_current=0,
    power_psm_array_voltage=0,

    # Telemetry
)

CAN_BUS: BusABC = MagicMock()

STEERING_WHEEL: SteeringWheel = MagicMock()

PEDALS_ADC78H89: ADC78H89 = MagicMock(
    sample_all=lambda *_: defaultdict(float),
)

UNUSED_SWITCH_PRBS: PRBS = 2, 0

LEFT_INDICATOR_LIGHT_SWITCH_PRBS: PRBS = 0, 2
RIGHT_INDICATOR_LIGHT_SWITCH_PRBS: PRBS = 0, 3
HAZARD_LIGHTS_SWITCH_PRBS: PRBS = 2, 0
DAYTIME_RUNNING_LIGHTS_SWITCH_PRBS: PRBS = 0, 5
HORN_SWITCH_PRBS: PRBS = 0, 4
BACKUP_CAMERA_CONTROL_SWITCH_PRBS: PRBS = 2, 0
BRAKE_SWITCH_GPIO: GPIO = MagicMock(read=lambda *_: False)

CRUISE_CONTROL_ROTARY_ENCODER_A_PRBS: PRBS = 2, 0
CRUISE_CONTROL_ROTARY_ENCODER_B_PRBS: PRBS = 2, 0
DIRECTION_SWITCH_PRBS: PRBS = 1, 1
REGENERATION_SWITCH_PRBS: PRBS = 0, 1
VARIABLE_FIELD_MAGNET_UP_SWITCH_PRBS: PRBS = 1, 3
VARIABLE_FIELD_MAGNET_DOWN_SWITCH_PRBS: PRBS = 1, 2
CRUISE_CONTROL_SWITCH_PRBS: PRBS = 0, 0
ACCELERATION_INPUT_INPUT_CHANNEL: InputChannel = InputChannel.AIN2

ARRAY_RELAY_SWITCH_PRBS: PRBS = 0, 6
BATTERY_RELAY_SWITCH_PRBS: PRBS = 0, 7

LEFT_INDICATOR_LIGHT_PWM: PWM = MagicMock()
RIGHT_INDICATOR_LIGHT_PWM: PWM = MagicMock()
DAYTIME_RUNNING_LIGHTS_PWM: PWM = MagicMock()
BRAKE_LIGHTS_PWM: PWM = MagicMock()

BACKUP_CAMERA_CONTROL_SWITCH_GPIO: GPIO = MagicMock()

ORIENTATION_IMU_BNO055: BNO055 = MagicMock(
    orientation=make_dataclass('', [])(),
)

POSITION_GPS: GPS = MagicMock()
LEFT_WHEEL_HALL_EFFECT: TMAG5273 = MagicMock()
RIGHT_WHEEL_HALL_EFFECT: TMAG5273 = MagicMock()
LEFT_WHEEL_ACCELEROMETER: LIS2HH12 = MagicMock()
RIGHT_WHEEL_ACCELEROMETER: LIS2HH12 = MagicMock()

ARRAY_RELAY_LOW_SIDE_GPIO: GPIO = MagicMock()
ARRAY_RELAY_HIGH_SIDE_GPIO: GPIO = MagicMock()
ARRAY_RELAY_PRE_CHARGE_GPIO: GPIO = MagicMock()
POWER_POINT_TRACKING_SWITCH_1_GPIO: GPIO = MagicMock()
POWER_POINT_TRACKING_SWITCH_2_GPIO: GPIO = MagicMock()

VARIABLE_FIELD_MAGNET_DIRECTION_GPIO: GPIO = MagicMock()
VARIABLE_FIELD_MAGNET_STALL_GPIO: GPIO = MagicMock()
VARIABLE_FIELD_MAGNET_ENCODER_A_GPIO: GPIO = MagicMock()
VARIABLE_FIELD_MAGNET_ENCODER_B_GPIO: GPIO = MagicMock()
VARIABLE_FIELD_MAGNET_ENABLE_GPIO: GPIO = MagicMock()

RADIO_SERIAL: Serial = MagicMock()

WAVESCULPTOR22: WaveSculptor22 = MagicMock()

BATTERY_MANAGEMENT_SYSTEM: BatteryManagementSystem = MagicMock()

PSM_MOTOR_INA229: INA229 = MagicMock()
PSM_BATTERY_INA229: INA229 = MagicMock()
PSM_ARRAY_INA229: INA229 = MagicMock()

PERIPHERIES: Peripheries = Peripheries(
    # General

    general_can_bus=CAN_BUS,

    # Debugger

    # Display

    # Driver

    driver_steering_wheel=STEERING_WHEEL,

    driver_pedals_adc78h89=PEDALS_ADC78H89,

    driver_general_unused_switch_prbs=UNUSED_SWITCH_PRBS,

    driver_miscellaneous_left_indicator_light_switch_prbs=(
        LEFT_INDICATOR_LIGHT_SWITCH_PRBS
    ),
    driver_miscellaneous_right_indicator_light_switch_prbs=(
        RIGHT_INDICATOR_LIGHT_SWITCH_PRBS
    ),
    driver_miscellaneous_hazard_lights_switch_prbs=HAZARD_LIGHTS_SWITCH_PRBS,
    driver_miscellaneous_daytime_running_lights_switch_prbs=(
        DAYTIME_RUNNING_LIGHTS_SWITCH_PRBS
    ),
    driver_miscellaneous_horn_switch_prbs=HORN_SWITCH_PRBS,
    driver_miscellaneous_backup_camera_control_switch_prbs=(
        BACKUP_CAMERA_CONTROL_SWITCH_PRBS
    ),
    driver_miscellaneous_brake_switch_gpio=BRAKE_SWITCH_GPIO,

    driver_motor_cruise_control_velocity_rotary_encoder_a_prbs=(
        CRUISE_CONTROL_ROTARY_ENCODER_A_PRBS
    ),
    driver_motor_cruise_control_velocity_rotary_encoder_b_prbs=(
        CRUISE_CONTROL_ROTARY_ENCODER_B_PRBS
    ),
    driver_motor_direction_switch_prbs=DIRECTION_SWITCH_PRBS,
    driver_motor_regeneration_switch_prbs=REGENERATION_SWITCH_PRBS,
    driver_motor_variable_field_magnet_up_switch_prbs=(
        VARIABLE_FIELD_MAGNET_UP_SWITCH_PRBS
    ),
    driver_motor_variable_field_magnet_down_switch_prbs=(
        VARIABLE_FIELD_MAGNET_DOWN_SWITCH_PRBS
    ),
    driver_motor_cruise_control_switch_prbs=CRUISE_CONTROL_SWITCH_PRBS,
    driver_motor_acceleration_input_input_channel=(
        ACCELERATION_INPUT_INPUT_CHANNEL
    ),

    driver_power_array_relay_switch_prbs=ARRAY_RELAY_SWITCH_PRBS,
    driver_power_battery_relay_switch_prbs=BATTERY_RELAY_SWITCH_PRBS,

    # Miscellaneous

    miscellaneous_left_indicator_light_pwm=LEFT_INDICATOR_LIGHT_PWM,
    miscellaneous_right_indicator_light_pwm=RIGHT_INDICATOR_LIGHT_PWM,
    miscellaneous_daytime_running_lights_pwm=DAYTIME_RUNNING_LIGHTS_PWM,
    miscellaneous_brake_lights_pwm=BRAKE_LIGHTS_PWM,
    miscellaneous_backup_camera_control_switch_gpio=(
        BACKUP_CAMERA_CONTROL_SWITCH_GPIO
    ),
    miscellaneous_orientation_imu_bno055=ORIENTATION_IMU_BNO055,
    miscellaneous_position_gps=POSITION_GPS,
    miscellaneous_left_wheel_hall_effect=LEFT_WHEEL_HALL_EFFECT,
    miscellaneous_right_wheel_hall_effect=RIGHT_WHEEL_HALL_EFFECT,
    miscellaneous_left_wheel_accelerometer=LEFT_WHEEL_ACCELEROMETER,
    miscellaneous_right_wheel_accelerometer=RIGHT_WHEEL_ACCELEROMETER,

    # Motor

    motor_wavesculptor22=WAVESCULPTOR22,
    motor_variable_field_magnet_direction_gpio=(
        VARIABLE_FIELD_MAGNET_DIRECTION_GPIO
    ),
    motor_variable_field_magnet_stall_gpio=VARIABLE_FIELD_MAGNET_STALL_GPIO,
    motor_variable_field_magnet_encoder_a_gpio=(
        VARIABLE_FIELD_MAGNET_ENCODER_A_GPIO
    ),
    motor_variable_field_magnet_encoder_b_gpio=(
        VARIABLE_FIELD_MAGNET_ENCODER_B_GPIO
    ),
    motor_variable_field_magnet_enable_gpio=VARIABLE_FIELD_MAGNET_ENABLE_GPIO,

    # Power

    power_array_relay_low_side_gpio=ARRAY_RELAY_LOW_SIDE_GPIO,
    power_array_relay_high_side_gpio=ARRAY_RELAY_HIGH_SIDE_GPIO,
    power_array_relay_pre_charge_gpio=ARRAY_RELAY_PRE_CHARGE_GPIO,
    power_point_tracking_switch_1_gpio=POWER_POINT_TRACKING_SWITCH_1_GPIO,
    power_point_tracking_switch_2_gpio=POWER_POINT_TRACKING_SWITCH_2_GPIO,
    power_battery_management_system=BATTERY_MANAGEMENT_SYSTEM,
    power_psm_motor_ina229=PSM_MOTOR_INA229,
    power_psm_battery_ina229=PSM_BATTERY_INA229,
    power_psm_array_ina229=PSM_ARRAY_INA229,

    # Telemetry

    telemetry_radio_serial=RADIO_SERIAL,
)

with open('data/battery.json') as file:
    BATTERY = Battery(**load(file))

SETTINGS: Settings = Settings(
    # General

    general_wheel_diameter=0.557,

    # Debugger

    # Display

    display_frame_rate=3,
    display_font_pathname='fonts/minecraft.ttf',

    # Driver

    driver_timeout=0.001,

    # Miscellaneous

    miscellaneous_light_timeout=0.1,
    miscellaneous_light_flash_timeout=0.5,
    miscellaneous_orientation_timeout=0.1,
    miscellaneous_position_timeout=1,
    miscellaneous_front_wheels_timeout=0.02,
    miscellaneous_acceleration_log_filepath='/',

    # Motor

    motor_control_timeout=0.1,
    motor_variable_field_magnet_timeout=0.1,

    motor_acceleration_input_max_increase=1,
    motor_acceleration_input_max_decrease=1,
    motor_bus_current_limit=0.7,
    motor_regeneration_strength=0.3,
    motor_variable_field_magnet_step_size=40,
    motor_variable_field_magnet_step_upper_limit=320,
    motor_variable_field_magnet_frequency=1000,
    motor_variable_field_magnet_duty_cycle=0.75,
    motor_variable_field_magnet_stall_threshold=20,
    motor_variable_field_magnet_max_enable_time_reset=15.0,
    motor_variable_field_magnet_max_enable_time_move=0.5,

    # Power

    power_monitor_timeout=0.1,
    power_array_relay_timeout=2.5,
    power_point_tracking_timeout=1.0,
    power_soc_timeout=0.05,
    power_psm_timeout=0.1,
    power_steering_wheel_led_timeout=0.5,
    power_battery=BATTERY,
    power_disable_charging_battery_soc_threshold=0.98,
    power_psm_motor_ina229_voltage_correction_factor=12.9,
    power_psm_battery_ina229_voltage_correction_factor=12.9,
    power_psm_array_ina229_voltage_correction_factor=12.9,
    power_battery_overcurrent_limit=60.0,
    power_battery_undercurrent_limit=-50.0,

    # Telemetry

    telemetry_timeout=0.2,
    telemetry_begin_token=b'',
    telemetry_separator_token=b'_',
    telemetry_end_token=b'\r\n',
)
