from abc import ABC
from concurrent.futures import ThreadPoolExecutor
from collections.abc import Callable
from dataclasses import dataclass, field
from multiprocessing import get_logger
from typing import ClassVar

from revolution.environment import Endpoint, Environment, Header, Message

_logger = get_logger()


@dataclass
class Application(ABC):
    @classmethod
    def main(cls, environment: Environment) -> None:
        application = cls(environment)
        application.mainloop()

    endpoint: ClassVar[Endpoint]
    _environment: Environment
    _thread_pool_executor: ThreadPoolExecutor \
        = field(default_factory=ThreadPoolExecutor, init=False)
    _handlers: dict[Header, Callable[..., None]] \
        = field(default_factory=dict, init=False)
    __status: bool = field(default=False, init=False)

    def mainloop(self) -> None:
        _logger.info('Starting...')

        self.__status = True

        self._setup()
        self.__run()

    def _setup(self) -> None:
        _logger.info('Setting up...')

        self._handlers[Header.STOP] = self.__handle_stop

    def __run(self) -> None:
        _logger.info('Running...')

        while self.__status:
            message = self._environment.receive(self.endpoint)

            self.__handle(message)

    def __handle(self, message: Message) -> None:
        self._handlers[message.header](*message.args, **message.kwargs)

    def __handle_stop(self) -> None:
        _logger.info('Stopping...')

        self.__status = False
