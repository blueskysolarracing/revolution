from math import inf
from typing import cast
from unittest.mock import MagicMock

from iclib.adc78h89 import ADC78H89, InputChannel
from iclib.mcp23s17 import MCP23S17, PortRegisterBit as PRB
from iclib.mcp4161 import MCP4161
from iclib.nhd_c12864a1z_fsw_fbw_htt import NHDC12864A1ZFSWFBWHTT
from iclib.utilities import ManualCSSPI
from periphery import GPIO, SPI

from revolution import (
    Application,
    Contexts,
    Debugger,
    Direction,
    Display,
    Driver,
    MC2,
    Miscellaneous,
    Motor,
    Peripheries,
    Power,
    Settings,
    Telemetry,
)

APPLICATION_TYPES: tuple[type[Application], ...] = (
    # Debugger,
    # Display,
    Driver,
    # Miscellaneous,
    Motor,
    Power,
    # Telemetry,
)

CONTEXTS: Contexts = Contexts(
    # Debugger

    # Display

    display_backup_camera_control_status_input=False,
    display_steering_wheel_in_place_status_input=False,
    display_left_directional_pad_input=False,
    display_right_directional_pad_input=False,
    display_up_directional_pad_input=False,
    display_down_directional_pad_input=False,
    display_center_directional_pad_input=False,

    # Driver

    # Miscellaneous

    miscellaneous_thermistor_temperature=0,
    miscellaneous_left_indicator_light_status_input=False,
    miscellaneous_right_indicator_light_status_input=False,
    miscellaneous_hazard_lights_status_input=False,
    miscellaneous_daytime_running_lights_status_input=False,
    miscellaneous_horn_status_input=False,
    miscellaneous_fan_status_input=False,
    miscellaneous_brake_status_input=False,

    # Motor

    motor_acceleration_pedal_input=0,
    motor_regeneration_pedal_input=0,
    motor_acceleration_paddle_input=0,
    motor_regeneration_paddle_input=0,
    motor_acceleration_cruise_control_input=0,
    motor_regeneration_cruise_control_input=0,
    motor_status_input=False,
    motor_direction_input=Direction.FORWARD,
    motor_economical_mode_input=True,
    motor_variable_field_magnet_up_input=0,
    motor_variable_field_magnet_down_input=0,
    motor_revolution_period=inf,
    motor_speed=0,
    motor_cruise_control_speed=None,

    # Power

    power_array_relay_status_input=False,
    power_battery_relay_status_input=False,
    power_state_of_charge=0,

    # Telemetry
)

mc2_spi = SPI('/dev/spidev1.0', 3, 1e6)
mc2: MC2 = MC2(
    MCP4161(
        cast(
            SPI,
            ManualCSSPI(
                GPIO('/dev/gpiochip5', 29, 'out', inverted=True),
                mc2_spi,
            ),
        )
    ),
    MCP4161(
        cast(
            SPI,
            ManualCSSPI(
                GPIO('/dev/gpiochip5', 28, 'out', inverted=True),
                mc2_spi,
            ),
        ),
    ),
    GPIO('/dev/gpiochip6', 14, 'out', inverted=True),
    GPIO('/dev/gpiochip6', 13, 'out'),
    GPIO('/dev/gpiochip6', 11, 'out'),
    GPIO('/dev/gpiochip6', 12, 'out'),
    GPIO('/dev/gpiochip6', 10, 'out'),
    GPIO('/dev/gpiochip6', 17, 'out'),
    MagicMock(edge='both', inverted=False),
)

PERIPHERIES: Peripheries = Peripheries(
    # Debugger

    # Display

    display_nhd_c12864a1z_fsw_fbw_htt=NHDC12864A1ZFSWFBWHTT(
        MagicMock(mode=0b11, max_speed=1e6, bit_order='msb', extra_flags=None),
        MagicMock(),
        MagicMock(),
        # GPIO('/dev/gpiochip3', 6, 'out')
    ),

    # Driver

    # TODO: put proper input channel/port-register-bit (prb)

    driver_adc78h89=ADC78H89(
        MagicMock(
            mode=0b11,
            max_speed=1e6,
            bit_order='msb',
            bits_per_word=8,
            extra_flags=None,
            transfer=lambda data: [0] * len(data),
        ),
        3.3,
    ),

    driver_motor_acceleration_pedal_input_channel=InputChannel.AIN1,
    driver_motor_regeneration_pedal_input_channel=InputChannel.AIN1,
    driver_motor_acceleration_paddle_input_channel=InputChannel.AIN1,
    driver_motor_regeneration_paddle_input_channel=InputChannel.AIN1,
    driver_miscellaneous_thermistor_input_channel=InputChannel.AIN1,

    driver_mcp23s17=MCP23S17(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        cast(
            SPI,
            ManualCSSPI(
                GPIO('/dev/gpiochip3', 5, 'out', inverted=True),
                SPI('/dev/spidev0.0', 0b11, 1e6),
            ),
        ),
    ),

    driver_motor_direction_switch_prb=PRB.GPIOB_GP3,
    driver_motor_variable_field_magnet_up_switch_prb=PRB.GPIOA_GP0,
    driver_motor_variable_field_magnet_down_switch_prb=PRB.GPIOA_GP0,

    driver_miscellaneous_left_indicator_light_switch_prb=PRB.GPIOA_GP0,
    driver_miscellaneous_right_indicator_light_switch_prb=PRB.GPIOA_GP0,
    driver_miscellaneous_hazard_lights_switch_prb=PRB.GPIOA_GP0,
    driver_miscellaneous_daytime_running_lights_switch_prb=PRB.GPIOA_GP0,
    driver_miscellaneous_horn_switch_prb=PRB.GPIOA_GP0,
    driver_miscellaneous_fan_switch_prb=PRB.GPIOA_GP0,
    driver_miscellaneous_backup_camera_control_switch_prb=PRB.GPIOA_GP0,
    driver_miscellaneous_brake_pedal_switch_prb=PRB.GPIOA_GP0,

    driver_power_array_relay_switch_prb=PRB.GPIOA_GP6,
    driver_power_battery_relay_switch_prb=PRB.GPIOA_GP5,

    driver_display_steering_wheel_in_place_switch_prb=PRB.GPIOA_GP0,
    driver_display_left_directional_pad_switch_prb=PRB.GPIOA_GP0,
    driver_display_right_directional_pad_switch_prb=PRB.GPIOA_GP0,
    driver_display_up_directional_pad_switch_prb=PRB.GPIOA_GP0,
    driver_display_down_directional_pad_switch_prb=PRB.GPIOA_GP0,
    driver_display_center_directional_pad_switch_prb=PRB.GPIOA_GP0,

    # Miscellaneous

    miscellaneous_indicator_lights_pwm=MagicMock(),
    miscellaneous_left_indicator_light_pwm=MagicMock(),
    miscellaneous_right_indicator_light_pwm=MagicMock(),
    miscellaneous_daytime_running_lights_pwm=MagicMock(),
    miscellaneous_brake_lights_pwm=MagicMock(),
    miscellaneous_horn_switch_gpio=MagicMock(),
    miscellaneous_fan_switch_gpio=MagicMock(),

    # Motor

    motor_mc2=mc2,

    # Power

    power_pptmb_spi=MagicMock(),
    power_bms_spi=MagicMock(),
    power_battery_relay_ls_gpio=GPIO('/dev/gpiochip4', 2, 'out'),
    power_battery_relay_hs_gpio=GPIO('/dev/gpiochip3', 26, 'out'),
    power_battery_relay_pc_gpio=GPIO('/dev/gpiochip3', 28, 'out'),

    # Telemetry

    telemetry_serial=MagicMock(),
)

SETTINGS: Settings = Settings(
    # Debugger

    # Display

    display_frame_rate=10,
    display_font_pathname='fonts/minecraft.ttf',

    # Driver

    driver_timeout=0.01,

    # TODO: put proper values below

    driver_motor_acceleration_pedal_input_range=(0, 1),
    driver_motor_regeneration_pedal_input_range=(0, 1),
    driver_motor_acceleration_paddle_input_range=(0, 1),
    driver_motor_regeneration_paddle_input_range=(0, 1),
    driver_miscellaneous_thermistor_input_range=(0, 1),
    driver_miscellaneous_thermistor_output_range=(0, 1),

    # Miscellaneous

    miscellaneous_indicator_lights_pwm_period=0.8,
    miscellaneous_indicator_lights_pwm_duty_cycle=0.5,
    miscellaneous_left_indicator_light_pwm_period=0.001,
    miscellaneous_left_indicator_light_pwm_duty_cycle=0.25,
    miscellaneous_right_indicator_light_pwm_period=0.001,
    miscellaneous_right_indicator_light_pwm_duty_cycle=0.25,
    miscellaneous_daytime_running_lights_pwm_period=0.001,
    miscellaneous_daytime_running_lights_pwm_duty_cycle=0.25,
    miscellaneous_brake_lights_pwm_period=0.001,
    miscellaneous_brake_lights_pwm_duty_cycle=0.25,

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
