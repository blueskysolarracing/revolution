from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from multiprocessing import Queue, get_logger
from typing import Any

from revolution.data import DataManager

_logger = get_logger()


class Header(Enum):
    STOP = auto()
    DEBUG = auto()


@dataclass
class Message:
    header: Header
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)


class Direction(IntEnum):
    UP = 2
    DOWN = 3
    LEFT = 5
    RIGHT = 7
    FORWARD = 11
    BACKWARD = 13


@dataclass
class Context:
    # Motor
    motor_direction_input: Direction = Direction.FORWARD
    acceleration_input: float = 0
    regeneration_input: float = 0
    eco_status_input: bool = False
    gear_index_input_counter: int = 0

    # Miscellaneous
    horn_status_input: bool = False
    left_indicator_status_input: bool = False
    right_indicator_status_input: bool = False
    hazard_lights_status_input: bool = False
    daytime_running_light_status_input: bool = False
    display_backlight_status_input: bool = False

    # Battery
    battery_relay_status: bool = False
    battery_relay_status_input: int = 0
    array_relay_status_input: int = 0

    # Unclassified
    brake_status_input: float = 0
    backup_camera_control_status_input: int = 0
    fan_status_input: int = 0
    directional_pad_input: Direction | None = None
    radio_status_input: bool = False
    steering_wheel_in_place_status_input: bool = False
    thermistor_status_input: int = False


class Endpoint(Enum):
    DISPLAY = auto()
    MOTOR = auto()
    STEERING_WHEEL = auto()
    DEBUGGER = auto()


@dataclass
class Environment(DataManager[Context]):
    __queues: dict[Endpoint, Queue[Message]] \
        = field(default_factory=dict, init=False)

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
