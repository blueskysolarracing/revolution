from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from logging import getLogger
from math import inf
from queue import Queue
from typing import Any

from revolution.data import DataManager

_logger = getLogger(__name__)


class Header(Enum):
    STOP = auto()
    DEBUG = auto()


class Endpoint(Enum):
    DISPLAY = auto()
    MISCELLANEOUS = auto()
    MOTOR = auto()
    STEERING_WHEEL = auto()
    DEBUGGER = auto()


class DirectionalPad(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    CENTER = auto()


class Direction(IntEnum):
    FORWARD = 0
    BACKWARD = 1


@dataclass
class Context:
    # Motor
    acceleration_pedal_input: float = 0
    regeneration_pedal_input: float = 0
    acceleration_paddle_input: float = 0
    regeneration_paddle_input: float = 0
    motor_status_input: bool = False
    direction_input: Direction = Direction.FORWARD
    economical_mode_input: bool = True
    variable_field_magnet_up_input: int = 0
    variable_field_magnet_down_input: int = 0
    revolution_period: float = inf

    # Miscellaneous
    left_indicator_light_status_input: bool = False
    right_indicator_light_status_input: bool = False
    hazard_lights_status_input: bool = False
    daytime_running_lights_status_input: bool = False
    horn_status_input: bool = False
    fan_status_input: bool = False

    # Power
    array_relay_status_input: bool = False
    battery_relay_status_input: bool = False

    # Display
    thermistor_input: float = 0
    backup_camera_control_status_input: bool = False
    steering_wheel_in_place_status_input: bool = False
    left_directional_pad_input: bool = False
    right_directional_pad_input: bool = False
    up_directional_pad_input: bool = False
    down_directional_pad_input: bool = False
    center_directional_pad_input: bool = False
    # Display data placeholders
    solar_power: float = 0
    solar_voltage: float = 0
    solar_current: float = 0
    motor_power: float = 0
    motor_voltage: float = 0
    motor_current: float = 0
    battery_power: float = 0
    battery_voltage: float = 0
    battery_current: float = 0
    battery_soc: float = 0
    speed_kph: float = 0
    motor_state: int = 0  # 0=OFF, 1=PEDAL, 2=CRUISE, 3=REGEN
    vfm: int = 0
    battery_volt: float = 0
    battery_low_volt_power: float = 0
    battery_low_volt_voltage: float = 0
    battery_low_volt_current: float = 0
    battery_high_volt_voltage: float = 0
    max_package_temp: float = 0
    bms_fault_type: int = 0  # 0=OVERTEMP, 1=OVERVOLT, 2=UNDERVOLT, 3=OVERCUR
    fault_therm: int = 0
    fault_cell: int = 0
    # Display flags placeholders
    cruise: bool = False
    ignition: bool = False
    bms_fault: bool = False
    battery_warning: bool = False
    battery_low_volt: bool = False
    bb_status: bool = True
    mc_status: bool = True
    bms_status: bool = True
    ppt_status: bool = True
    rad_status: bool = True
    # less important display flags
    eco_mode: bool = False  # eco mode that draws leaf symbol on d1
    direction: bool = True  # direction of the car, True is forward, else rev
    headlight: bool = False  # whether headlights are on
    # might have replacement but for display
    hazard_lights_status: bool = False
    left_indicator_light_status: bool = False
    right_indicator_light_status: bool = False

    # Unclassified
    brake_status_input: bool = False
    debug: Any = None


@dataclass
class Message:
    header: Header
    args: tuple[Any, ...] = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class Environment(DataManager[Context]):
    __queues: dict[Endpoint, Queue[Message]] \
        = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        for endpoint in Endpoint:
            self.__queues[endpoint] = Queue()

    def receive_message(
            self,
            endpoint: Endpoint,
            block: bool = True,
            timeout: float | None = None,
    ) -> Message:
        return self.__queues[endpoint].get(block, timeout)

    def send_message(
            self,
            endpoint: Endpoint,
            message: Message,
            block: bool = True,
            timeout: float | None = None,
    ) -> None:
        self.__queues[endpoint].put(message, block, timeout)
