from dataclasses import asdict, dataclass, field
from enum import auto, Enum
from json import dumps
from logging import getLogger
from queue import Queue
from typing import Any

from door.threading2 import AcquirableDoor
from iclib.adc78h89 import ADC78H89, InputChannel
from iclib.mcp23s17 import MCP23S17, PortRegisterBit as PRB
from iclib.nhd_c12864a1z_fsw_fbw_htt import NHDC12864A1ZFSWFBWHTT
from periphery import GPIO, PWM, Serial, SPI

from revolution.mc2 import MC2
from revolution.utilities import Direction

_logger = getLogger(__name__)


class Endpoint(Enum):
    DEBUGGER = auto()
    DISPLAY = auto()
    DRIVER = auto()
    MISCELLANEOUS = auto()
    MOTOR = auto()
    POWER = auto()
    TELEMETER = auto()


class Header(Enum):
    STOP = auto()


@dataclass(frozen=True)
class Message:
    header: Header
    args: tuple[Any, ...] = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class Contexts:
    # Debugger

    # Display

    display_backup_camera_control_status_input: bool
    display_steering_wheel_in_place_status_input: bool
    display_left_directional_pad_input: bool
    display_right_directional_pad_input: bool
    display_up_directional_pad_input: bool
    display_down_directional_pad_input: bool
    display_center_directional_pad_input: bool

    # Driver

    # Miscellaneous

    miscellaneous_thermistor_temperature: float
    miscellaneous_left_indicator_light_status_input: bool
    miscellaneous_right_indicator_light_status_input: bool
    miscellaneous_hazard_lights_status_input: bool
    miscellaneous_daytime_running_lights_status_input: bool
    miscellaneous_horn_status_input: bool
    miscellaneous_fan_status_input: bool
    miscellaneous_brake_status_input: bool

    # Motor

    motor_acceleration_pedal_input: float
    motor_regeneration_pedal_input: float
    motor_acceleration_paddle_input: float
    motor_regeneration_paddle_input: float
    motor_acceleration_cruise_control_input: float
    motor_regeneration_cruise_control_input: float
    motor_status_input: bool
    motor_direction_input: Direction
    motor_economical_mode_input: bool
    motor_variable_field_magnet_up_input: int
    motor_variable_field_magnet_down_input: int
    motor_revolution_period: float
    motor_speed: float
    motor_cruise_control_speed: float | None

    # Power

    power_array_relay_status_input: bool
    power_battery_relay_status_input: bool
    power_state_of_charge: float

    # Telemetry

    def serialize(self) -> str:
        return dumps(asdict(self))


@dataclass(frozen=True)
class Peripheries:
    # Debugger

    # Display

    display_nhd_c12864a1z_fsw_fbw_htt: NHDC12864A1ZFSWFBWHTT
    """The NHD display."""

    # Driver

    driver_adc78h89: ADC78H89

    driver_motor_acceleration_pedal_input_channel: InputChannel
    driver_motor_regeneration_pedal_input_channel: InputChannel
    driver_motor_acceleration_paddle_input_channel: InputChannel
    driver_motor_regeneration_paddle_input_channel: InputChannel
    driver_miscellaneous_thermistor_input_channel: InputChannel

    driver_mcp23s17: MCP23S17

    driver_motor_direction_switch_prb: PRB
    driver_motor_variable_field_magnet_up_switch_prb: PRB
    driver_motor_variable_field_magnet_down_switch_prb: PRB

    driver_miscellaneous_left_indicator_light_switch_prb: PRB
    driver_miscellaneous_right_indicator_light_switch_prb: PRB
    driver_miscellaneous_hazard_lights_switch_prb: PRB
    driver_miscellaneous_daytime_running_lights_switch_prb: PRB
    driver_miscellaneous_horn_switch_prb: PRB
    driver_miscellaneous_fan_switch_prb: PRB
    driver_miscellaneous_backup_camera_control_switch_prb: PRB
    driver_miscellaneous_brake_pedal_switch_prb: PRB

    driver_power_array_relay_switch_prb: PRB
    driver_power_battery_relay_switch_prb: PRB

    driver_display_steering_wheel_in_place_switch_prb: PRB
    driver_display_left_directional_pad_switch_prb: PRB
    driver_display_right_directional_pad_switch_prb: PRB
    driver_display_up_directional_pad_switch_prb: PRB
    driver_display_down_directional_pad_switch_prb: PRB
    driver_display_center_directional_pad_switch_prb: PRB

    # Miscellaneous

    miscellaneous_indicator_lights_pwm: PWM
    miscellaneous_left_indicator_light_pwm: PWM
    miscellaneous_right_indicator_light_pwm: PWM
    miscellaneous_daytime_running_lights_pwm: PWM
    miscellaneous_brake_lights_pwm: PWM
    miscellaneous_horn_switch_gpio: GPIO
    miscellaneous_fan_switch_gpio: GPIO

    # Motor

    motor_mc2: MC2

    # Power

    power_pptmb_spi: SPI
    power_bms_spi: SPI
    power_battery_relay_ls_gpio: GPIO
    power_battery_relay_hs_gpio: GPIO
    power_battery_relay_pc_gpio: GPIO

    # Telemetry

    telemetry_serial: Serial


@dataclass(frozen=True)
class Settings:
    # Debugger

    # Display

    display_frame_rate: float
    """The display frame rate (in frames/second)."""
    display_font_pathname: str
    """The display font pathname (.ttf file)."""

    # Driver

    driver_timeout: float

    driver_motor_acceleration_pedal_input_range: tuple[float, float]
    driver_motor_regeneration_pedal_input_range: tuple[float, float]
    driver_motor_acceleration_paddle_input_range: tuple[float, float]
    driver_motor_regeneration_paddle_input_range: tuple[float, float]
    driver_miscellaneous_thermistor_input_range: tuple[float, float]
    driver_miscellaneous_thermistor_output_range: tuple[float, float]

    # Miscellaneous

    miscellaneous_indicator_lights_pwm_period: float
    miscellaneous_indicator_lights_pwm_duty_cycle: float
    miscellaneous_left_indicator_light_pwm_period: float
    miscellaneous_left_indicator_light_pwm_duty_cycle: float
    miscellaneous_right_indicator_light_pwm_period: float
    miscellaneous_right_indicator_light_pwm_duty_cycle: float
    miscellaneous_daytime_running_lights_pwm_period: float
    miscellaneous_daytime_running_lights_pwm_duty_cycle: float
    miscellaneous_brake_lights_pwm_period: float
    miscellaneous_brake_lights_pwm_duty_cycle: float

    miscellaneous_light_timeout: float

    # Motor

    motor_wheel_circumference: float
    motor_control_timeout: float
    motor_variable_field_magnet_timeout: float
    motor_revolution_timeout: float

    motor_cruise_control_k_p: float
    motor_cruise_control_k_i: float
    motor_cruise_control_k_d: float
    motor_cruise_control_min_integral: float
    motor_cruise_control_max_integral: float
    motor_cruise_control_min_derivative: float
    motor_cruise_control_max_derivative: float
    motor_cruise_control_min_output: float
    motor_cruise_control_max_output: float
    motor_cruise_control_timeout: float

    # Power

    power_monitor_timeout: float
    power_battery_relay_timeout: float

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
