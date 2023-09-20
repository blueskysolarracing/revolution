from dataclasses import dataclass, field
from enum import auto, Enum
from logging import getLogger
from typing import Any, TypeAlias

_logger = getLogger(__name__)
FloatRange: TypeAlias = tuple[float, float]


class Direction(Enum):
    FORWARD = auto()
    BACKWARD = auto()


class Endpoint(Enum):
    DEBUGGER = auto()
    DISPLAY = auto()
    MISCELLANEOUS = auto()
    MOTOR = auto()
    POWER = auto()
    STEERING_WHEEL = auto()
    TELEMETER = auto()


class Header(Enum):
    STOP = auto()


@dataclass(frozen=True)
class Message:
    header: Header
    args: tuple[Any, ...] = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
