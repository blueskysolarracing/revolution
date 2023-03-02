from abc import ABC
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from logging import getLogger
from queue import Empty
from typing import ClassVar

from revolution.environment import Endpoint, Environment, Header

_logger = getLogger(__name__)


@dataclass
class Application(ABC):
    @classmethod
    def main(cls, environment: Environment) -> None:
        application = cls(environment)
        application.mainloop()

    endpoint: ClassVar[Endpoint | None] = None
    _message_queue_timeout: ClassVar[float | None] = 1
    _environment: Environment
    _handlers: dict[Header, Callable[..., None]] \
        = field(default_factory=dict, init=False)
    _thread_pool_executor: ThreadPoolExecutor \
        = field(default_factory=ThreadPoolExecutor, init=False)

    def mainloop(self) -> None:
        _logger.info('Starting...')

        self._setup()
        self._teardown()

    @property
    def _status(self) -> bool:
        with self._environment.read() as data:
            return data.status

    def _setup(self) -> None:
        _logger.info('Setting up...')

        self._thread_pool_executor.submit(self.__handle_messages)

    def _teardown(self) -> None:
        self._thread_pool_executor.shutdown()

        _logger.info('Tearing down...')

    def __handle_messages(self) -> None:
        assert self.endpoint is not None

        _logger.info('Handling messages...')

        while self._status:
            try:
                message = self._environment.receive_message(
                    self.endpoint,
                    timeout=self._message_queue_timeout,
                )
            except Empty:
                message = None

            if message is not None:
                _logger.info(f'Handling message {message}...')

                handler = self._handlers.get(message.header)

                if handler is None:
                    _logger.error(f'Unable to handle message {message}')
                else:
                    handler(*message.args, **message.kwargs)
