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
