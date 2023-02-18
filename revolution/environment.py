from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
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


@dataclass
class Context:
    pass


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
