from dataclasses import dataclass, field
from enum import auto, Enum
from logging import getLogger
from queue import Queue
from typing import Any

from door.threading2 import AcquirableDoor

_logger = getLogger(__name__)


class Direction(Enum):
    FORWARD = auto()
    BACKWARD = auto()


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

    # Miscellaneous

    # Motor

    # Power

    # Steering wheel

    # Telemeter

    # General

    pass


@dataclass(frozen=True)
class Peripheries:
    # Debugger

    # Display

    # Miscellaneous

    # Motor

    # Power

    # Steering wheel

    # Telemeter

    # General

    pass


@dataclass(frozen=True)
class Settings:
    # Debugger

    # Display

    # Miscellaneous

    # Motor

    # Power

    # Steering wheel

    # Telemeter

    # General

    pass


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
