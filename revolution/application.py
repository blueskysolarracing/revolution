from abc import ABC
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from logging import getLogger
from queue import Empty
from typing import ClassVar

from revolution.environment import Endpoint, Environment, Header, Message

_logger = getLogger(__name__)


@dataclass
class Application(ABC):
    @classmethod
    def main(cls, environment: Environment) -> None:
        application = cls(environment)
        application.mainloop()

    endpoint: ClassVar[Endpoint | None] = None
    _timeout: ClassVar[float | None] = 1
    _environment: Environment
    _thread_pool_executor: ThreadPoolExecutor \
        = field(default_factory=ThreadPoolExecutor, init=False)
    _handlers: dict[Header, Callable[..., None]] \
        = field(default_factory=dict, init=False)

    @property
    def _status(self) -> bool:
        with self._environment.read() as data:
            return data.status

    def mainloop(self) -> None:
        _logger.info('Starting...')

        self._setup()
        self.__run()
        self._teardown()

    def _setup(self) -> None:
        _logger.info('Setting up...')

    def _teardown(self) -> None:
        _logger.info('Tearing down...')

    def __run(self) -> None:
        assert self.endpoint is not None

        _logger.info('Running...')

        while self._status:
            try:
                message = self._environment.receive(
                    self.endpoint,
                    timeout=self._timeout,
                )
            except Empty:
                message = None

            if message is not None:
                self.__handle(message)

    def __handle(self, message: Message) -> None:
        _logger.info(f'Handling message {message}...')

        handler = self._handlers.get(message.header)

        if handler is None:
            _logger.error(f'Unable to handle message {message}')
        else:
            handler(*message.args, **message.kwargs)
