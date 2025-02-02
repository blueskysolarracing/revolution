from typing import cast
from unittest.mock import MagicMock

from iclib.mcp23s17 import MCP23S17, PortRegisterBit as PRB
from iclib.mcp4161 import MCP4161
from iclib.nhd_c12864a1z_fsw_fbw_htt import NHDC12864A1ZFSWFBWHTT
from iclib.utilities import LockedSPI, ManualCSSPI
from periphery import GPIO, PWM, Serial, SPI

from revolution import (
    Application,
    Contexts,
    Debugger,
    Direction,
    # Display,
    Driver,
    # Miscellaneous,
    Motor,
    MotorControllerSquared,
    Peripheries,
    Power,
    PRBS,
    Settings,
    Telemetry,
)

APPLICATION_TYPES: tuple[type[Application], ...] = (
    Debugger,
    # Display,
    Driver,
    # Miscellaneous,
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

    motor_acceleration_input=0,
    motor_regeneration_input=0,
    motor_cruise_control_acceleration_input=0,
    motor_cruise_control_regeneration_input=0,
    motor_status_input=False,
    motor_direction_input=Direction.FORWARD,
    motor_economical_mode_input=True,
    motor_variable_field_magnet_up_input=0,
    motor_variable_field_magnet_down_input=0,
    motor_speed=0,
    motor_cruise_control_status_input=False,
    motor_cruise_control_speed=0,

    # Power

    power_array_relay_status_input=False,
    power_battery_relay_status_input=False,
    power_state_of_charge=0,

    # Telemetry
)

STEERING_WHEEL_SPI: SPI = cast(
    SPI,
    LockedSPI(SPI('/dev/spidev0.0', 0b11, 1e6)),
)

STEERING_WHEEL_MCP23S17: MCP23S17 = MCP23S17(
    MagicMock(),
    MagicMock(),
    MagicMock(),
    cast(
        SPI,
        ManualCSSPI(
            GPIO('/dev/gpiochip3', 5, 'out', inverted=True),
            STEERING_WHEEL_SPI,
        ),
    ),
)

NHD_C12864A1Z_FSW_FBW_HTT: NHDC12864A1ZFSWFBWHTT = (
    NHDC12864A1ZFSWFBWHTT(
        cast(
            SPI,
            ManualCSSPI(
                MagicMock(inverted=True),  # TODO
                STEERING_WHEEL_SPI,
            ),
        ),
        MagicMock(direction='out', inverted=False),  # PRB.GPIOA_GP5
        MagicMock(direction='out', inverted=True),  # PRB.GPIOA_GP6
    )
)

SHIFT_SWITCH_PRB: PRB = PRB.GPIOB_GP4

LEFT_INDICATOR_LIGHT_SWITCH_PRBS: PRBS = PRB.GPIOB_GP0
RIGHT_INDICATOR_LIGHT_SWITCH_PRBS: PRBS = PRB.GPIOA_GP7
HAZARD_LIGHTS_SWITCH_PRBS: PRBS = PRB.GPIOB_GP7, True
DAYTIME_RUNNING_LIGHTS_SWITCH_PRBS: PRBS = PRB.GPIOA_GP1, True
HORN_SWITCH_PRBS: PRBS = PRB.GPIOB_GP7, False
BACKUP_CAMERA_CONTROL_SWITCH_PRBS: PRBS = PRB.GPIOA_GP0, True
DISPLAY_BACKLIGHT_SWITCH_PRBS: PRBS = PRB.GPIOA_GP1, False
BRAKE_SWITCH_GPIO: GPIO = GPIO('/dev/gpiochip6', 20, 'in', inverted=True)

ACCELERATION_INPUT_ROTARY_ENCODER_A_PRBS: PRBS = PRB.GPIOA_GP2
ACCELERATION_INPUT_ROTARY_ENCODER_B_PRBS: PRBS = PRB.GPIOA_GP3
DIRECTION_SWITCH_PRBS: PRBS = PRB.GPIOB_GP3
REGENERATION_SWITCH_PRBS: PRBS = PRB.GPIOA_GP0, False
VARIABLE_FIELD_MAGNET_UP_SWITCH_PRBS: PRBS = PRB.GPIOB_GP2
VARIABLE_FIELD_MAGNET_DOWN_SWITCH_PRBS: PRBS = PRB.GPIOB_GP1
CRUISE_CONTROL_SWITCH_PRBS: PRBS = PRB.GPIOA_GP4

ARRAY_RELAY_SWITCH_PRBS: PRBS = PRB.GPIOA_GP6
BATTERY_RELAY_SWITCH_PRBS: PRBS = PRB.GPIOA_GP5

INDICATOR_LIGHTS_PWM: PWM = MagicMock()  # TODO
INDICATOR_LIGHTS_PWM.period = 0.8
INDICATOR_LIGHTS_PWM.duty_cycle = 0.5

LEFT_INDICATOR_LIGHT_PWM: PWM = MagicMock()  # TODO
LEFT_INDICATOR_LIGHT_PWM.period = 0.001
LEFT_INDICATOR_LIGHT_PWM.duty_cycle = 0.25

RIGHT_INDICATOR_LIGHT_PWM: PWM = MagicMock()  # TODO
RIGHT_INDICATOR_LIGHT_PWM.period = 0.001
RIGHT_INDICATOR_LIGHT_PWM.duty_cycle = 0.25

DAYTIME_RUNNING_LIGHTS_PWM: PWM = MagicMock()  # TODO
DAYTIME_RUNNING_LIGHTS_PWM.period = 0.001
DAYTIME_RUNNING_LIGHTS_PWM.duty_cycle = 0.25

BRAKE_LIGHTS_PWM: PWM = MagicMock()  # TODO
BRAKE_LIGHTS_PWM.period = 0.001
BRAKE_LIGHTS_PWM.duty_cycle = 0.25

HORN_SWITCH_GPIO: GPIO = MagicMock()  # TODO
BACKUP_CAMERA_CONTROL_SWITCH_GPIO: GPIO = MagicMock()  # TODO
DISPLAY_BACKLIGHT_SWITCH_GPIO: GPIO = GPIO('/dev/gpiochip3', 6, 'out')

MOTOR_CONTROLLER_SQUARED_SPI = SPI('/dev/spidev1.0', 3, 1e6)
MOTOR_CONTROLLER_SQUARED: MotorControllerSquared = MotorControllerSquared(
    MCP4161(
        cast(
            SPI,
            ManualCSSPI(
                GPIO('/dev/gpiochip5', 29, 'out', inverted=True),
                MOTOR_CONTROLLER_SQUARED_SPI,
            ),
        )
    ),
    MCP4161(
        cast(
            SPI,
            ManualCSSPI(
                GPIO('/dev/gpiochip5', 28, 'out', inverted=True),
                MOTOR_CONTROLLER_SQUARED_SPI,
            ),
        ),
    ),
    GPIO('/dev/gpiochip6', 14, 'out', inverted=True),
    GPIO('/dev/gpiochip6', 13, 'out'),
    GPIO('/dev/gpiochip6', 11, 'out'),
    GPIO('/dev/gpiochip6', 17, 'out'),
    GPIO('/dev/gpiochip6', 12, 'out'),
    GPIO('/dev/gpiochip6', 10, 'out'),
    GPIO('/dev/gpiochip4', 17, 'in', edge='both'),
)

BATTERY_RELAY_LS_GPIO: GPIO = GPIO('/dev/gpiochip4', 2, 'out')
BATTERY_RELAY_HS_GPIO: GPIO = GPIO('/dev/gpiochip3', 26, 'out')
BATTERY_RELAY_PC_GPIO: GPIO = GPIO('/dev/gpiochip3', 28, 'out')

RADIO_SERIAL: Serial = MagicMock()  # TODO

PERIPHERIES: Peripheries = Peripheries(
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

    motor_controller_squared=MOTOR_CONTROLLER_SQUARED,

    # Power

    power_battery_relay_ls_gpio=BATTERY_RELAY_LS_GPIO,
    power_battery_relay_hs_gpio=BATTERY_RELAY_HS_GPIO,
    power_battery_relay_pc_gpio=BATTERY_RELAY_PC_GPIO,

    # Telemetry

    telemetry_radio_serial=RADIO_SERIAL,
)

SETTINGS: Settings = Settings(
    # Debugger

    # Display

    display_frame_rate=10,
    display_font_pathname='fonts/minecraft.ttf',

    # Driver

    driver_timeout=0.001,
    driver_acceleration_input_step=0.1,

    # Miscellaneous

    miscellaneous_light_timeout=0.1,

    # Motor

    motor_wheel_circumference=1,
    motor_control_timeout=0.01,
    motor_variable_field_magnet_timeout=0.1,
    motor_revolution_timeout=0.5,

    motor_cruise_control_k_p=250,
    motor_cruise_control_k_i=15000,
    motor_cruise_control_k_d=0,
    motor_cruise_control_min_integral=-200,
    motor_cruise_control_max_integral=200,
    motor_cruise_control_min_derivative=-100,
    motor_cruise_control_max_derivative=100,
    motor_cruise_control_min_output=-255,
    motor_cruise_control_max_output=255,
    motor_cruise_control_timeout=0.02,

    # Power

    power_monitor_timeout=0.1,
    power_battery_relay_timeout=3,

    # Telemetry

    telemetry_timeout=1,
    telemetry_begin_token=b'__BEGIN__',
    telemetry_separator_token=b'__SEPARATOR__',
    telemetry_end_token=b'__END__',
)
