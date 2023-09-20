from dataclasses import dataclass, field
from logging import getLogger
from queue import Queue

from revolution.contexts import Contexts
from revolution.data import DataManager
from revolution.peripheries import Peripheries
from revolution.settings import Settings
from revolution.utilities import Endpoint, Message

_logger = getLogger(__name__)


@dataclass(frozen=True)
class Environment:
    contexts: DataManager[Contexts]
    peripheries: Peripheries
    settings: Settings
    __queues: dict[Endpoint, Queue[Message]] = field(
        default_factory=dict,
        init=False,
    )

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
