from unittest.mock import MagicMock

from battlib import Battery
from can import BusABC
from iclib.mcp23s17 import MCP23S17, PortRegisterBit as PRB
from iclib.nhd_c12864a1z_fsw_fbw_htt import NHDC12864A1ZFSWFBWHTT
from iclib.wavesculptor22 import WaveSculptor22
from json import load
from periphery import GPIO, PWM, Serial

from revolution import (  # noqa: F401
    Application,
    BATTERY_CELL_COUNT,
    BatteryManagementSystem,
    BATTERY_THERMISTOR_COUNT,
    Contexts,
    Debugger,
    Direction,
    Display,
    DriverControls,
    Miscellaneous,
    Motor,
    Peripheries,
    Power,
    PRBS,
    Settings,
    Telemetry,
)

APPLICATION_TYPES: tuple[type[Application], ...] = (
    Debugger,
    Display,
    DriverControls,
    Miscellaneous,
    Motor,
    Power,
    Telemetry,
)

CONTEXTS: Contexts = Contexts(
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
    miscellaneous_display_backlight_status_input=False,
    miscellaneous_brake_status_input=False,

    # Motor

    motor_status_input=False,
    motor_acceleration_input=0,
    motor_direction_input=Direction.FORWARD,
    motor_cruise_control_status_input=False,
    motor_cruise_control_velocity=0,
    motor_variable_field_magnet_up_input=0,
    motor_variable_field_magnet_down_input=0,
    motor_velocity=0,

    # Power

    power_array_relay_status_input=False,
    power_battery_relay_status_input=False,
    power_battery_cell_voltages=[0 for _ in range(BATTERY_CELL_COUNT)],
    power_battery_thermistor_temperatures=[
        0 for _ in range(BATTERY_THERMISTOR_COUNT)
    ],
    power_battery_bus_voltage=0,
    power_battery_current=0,
    power_battery_relay_status=False,
    power_battery_electric_safe_discharge_status=False,
    power_battery_discharge_status=False,
    power_battery_cell_flags=[0 for _ in range(BATTERY_CELL_COUNT)],
    power_battery_thermistor_flags=[
        0 for _ in range(BATTERY_THERMISTOR_COUNT)
    ],
    power_battery_current_flag=0,
    power_battery_state_of_charges=[0 for _ in range(BATTERY_CELL_COUNT)],

    # Telemetry
)

CAN_BUS: BusABC = MagicMock()

NHD_C12864A1Z_FSW_FBW_HTT: NHDC12864A1ZFSWFBWHTT = (
    NHDC12864A1ZFSWFBWHTT(
        MagicMock(mode=0b11, max_speed=1e6, bit_order='msb', extra_flags=None),
        MagicMock(direction='out', inverted=False),
        MagicMock(direction='out', inverted=True),
    )
)

STEERING_WHEEL_MCP23S17: MCP23S17 = MagicMock(
    read_register=lambda *_: [0xFF],
)

SHIFT_SWITCH_PRB: PRB = MagicMock()

LEFT_INDICATOR_LIGHT_SWITCH_PRBS: PRBS = PRB.GPIOB_GP0
RIGHT_INDICATOR_LIGHT_SWITCH_PRBS: PRBS = PRB.GPIOA_GP7
HAZARD_LIGHTS_SWITCH_PRBS: PRBS = PRB.GPIOB_GP7, True
DAYTIME_RUNNING_LIGHTS_SWITCH_PRBS: PRBS = PRB.GPIOA_GP1, True
HORN_SWITCH_PRBS: PRBS = PRB.GPIOB_GP7, False
BACKUP_CAMERA_CONTROL_SWITCH_PRBS: PRBS = PRB.GPIOA_GP0, True
DISPLAY_BACKLIGHT_SWITCH_PRBS: PRBS = PRB.GPIOA_GP1, False
BRAKE_SWITCH_GPIO: GPIO = MagicMock(read=lambda *_: False)

ACCELERATION_INPUT_ROTARY_ENCODER_A_PRBS: PRBS = PRB.GPIOA_GP2
ACCELERATION_INPUT_ROTARY_ENCODER_B_PRBS: PRBS = PRB.GPIOA_GP3
DIRECTION_SWITCH_PRBS: PRBS = PRB.GPIOB_GP3
REGENERATION_SWITCH_PRBS: PRBS = PRB.GPIOA_GP0, False
VARIABLE_FIELD_MAGNET_UP_SWITCH_PRBS: PRBS = PRB.GPIOB_GP2
VARIABLE_FIELD_MAGNET_DOWN_SWITCH_PRBS: PRBS = PRB.GPIOB_GP1
CRUISE_CONTROL_SWITCH_PRBS: PRBS = PRB.GPIOA_GP4

ARRAY_RELAY_SWITCH_PRBS: PRBS = PRB.GPIOA_GP0
BATTERY_RELAY_SWITCH_PRBS: PRBS = PRB.GPIOA_GP5

INDICATOR_LIGHTS_PWM: PWM = MagicMock()
LEFT_INDICATOR_LIGHT_PWM: PWM = MagicMock()
RIGHT_INDICATOR_LIGHT_PWM: PWM = MagicMock()
DAYTIME_RUNNING_LIGHTS_PWM: PWM = MagicMock()
BRAKE_LIGHTS_PWM: PWM = MagicMock()
HORN_SWITCH_GPIO: GPIO = MagicMock()
BACKUP_CAMERA_CONTROL_SWITCH_GPIO: GPIO = MagicMock()
DISPLAY_BACKLIGHT_SWITCH_GPIO: GPIO = MagicMock()

ARRAY_RELAY_LOW_SIDE_GPIO: GPIO = MagicMock()
ARRAY_RELAY_HIGH_SIDE_GPIO: GPIO = MagicMock()
ARRAY_RELAY_PRE_CHARGE_GPIO: GPIO = MagicMock()

RADIO_SERIAL: Serial = MagicMock()

WAVESCULPTOR22: WaveSculptor22 = MagicMock()

BATTERY_MANAGEMENT_SYSTEM: BatteryManagementSystem = MagicMock()

PERIPHERIES: Peripheries = Peripheries(
    # General

    can_bus=CAN_BUS,

    # Debugger

    # Display

    display_nhd_c12864a1z_fsw_fbw_htt=NHD_C12864A1Z_FSW_FBW_HTT,

    # Driver

    driver_steering_wheel_mcp23s17=STEERING_WHEEL_MCP23S17,

    driver_shift_switch_prb=SHIFT_SWITCH_PRB,

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
    driver_miscellaneous_display_backlight_switch_prbs=(
        DISPLAY_BACKLIGHT_SWITCH_PRBS
    ),
    driver_miscellaneous_brake_switch_gpio=BRAKE_SWITCH_GPIO,

    driver_motor_acceleration_input_rotary_encoder_a_prbs=(
        ACCELERATION_INPUT_ROTARY_ENCODER_A_PRBS
    ),
    driver_motor_acceleration_input_rotary_encoder_b_prbs=(
        ACCELERATION_INPUT_ROTARY_ENCODER_B_PRBS
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

    driver_power_array_relay_switch_prbs=ARRAY_RELAY_SWITCH_PRBS,
    driver_power_battery_relay_switch_prbs=BATTERY_RELAY_SWITCH_PRBS,

    # Miscellaneous

    miscellaneous_indicator_lights_pwm=INDICATOR_LIGHTS_PWM,
    miscellaneous_left_indicator_light_pwm=LEFT_INDICATOR_LIGHT_PWM,
    miscellaneous_right_indicator_light_pwm=RIGHT_INDICATOR_LIGHT_PWM,
    miscellaneous_daytime_running_lights_pwm=DAYTIME_RUNNING_LIGHTS_PWM,
    miscellaneous_brake_lights_pwm=BRAKE_LIGHTS_PWM,
    miscellaneous_horn_switch_gpio=HORN_SWITCH_GPIO,
    miscellaneous_backup_camera_control_switch_gpio=(
        BACKUP_CAMERA_CONTROL_SWITCH_GPIO
    ),
    miscellaneous_display_backlight_switch_gpio=DISPLAY_BACKLIGHT_SWITCH_GPIO,

    # Motor

    motor_wavesculptor22=WAVESCULPTOR22,

    # Power

    power_array_relay_low_side_gpio=ARRAY_RELAY_LOW_SIDE_GPIO,
    power_array_relay_high_side_gpio=ARRAY_RELAY_HIGH_SIDE_GPIO,
    power_array_relay_pre_charge_gpio=ARRAY_RELAY_PRE_CHARGE_GPIO,
    power_battery_management_system=BATTERY_MANAGEMENT_SYSTEM,

    # Telemetry

    telemetry_radio_serial=RADIO_SERIAL,
)

with open('data/battery.json') as file:
    BATTERY = Battery(**load(file))

SETTINGS: Settings = Settings(
    # General

    wheel_diameter=1,  # TODO

    # Debugger

    # Display

    display_frame_rate=10,
    display_font_pathname='fonts/minecraft.ttf',

    # Driver

    driver_timeout=0.01,
    driver_acceleration_input_step=0.1,

    # Miscellaneous

    miscellaneous_light_timeout=0.1,

    # Motor

    motor_control_timeout=0.1,
    motor_variable_field_magnet_timeout=0.1,

    # Power

    power_monitor_timeout=0.1,
    power_array_relay_timeout=2.5,
    power_soc_timeout=0.05,
    power_battery=BATTERY,

    # Telemetry

    telemetry_timeout=1,
    telemetry_begin_token=b'__BEGIN__',
    telemetry_separator_token=b'__SEPARATOR__',
    telemetry_end_token=b'__END__',
)
