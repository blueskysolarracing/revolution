from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass, field
from logging import getLogger
from queue import Empty
from typing import ClassVar, TypeVar

from revolution.environment import Endpoint, Environment, Header
from revolution.worker_pool import WorkerPool

_logger = getLogger(__name__)
_T = TypeVar('_T', bound='Application')


@dataclass
class Application(ABC):
    @classmethod
    def main(cls: type[_T], environment: Environment) -> _T:
        application = cls(environment)
        application.mainloop()

        return application

    endpoint: ClassVar[Endpoint | None] = None
    message_queue_timeout: ClassVar[float] = 0.1
    _environment: Environment
    _handlers: dict[Header, Callable[..., None]] \
        = field(default_factory=dict, init=False)
    _worker_pool: WorkerPool = field(default_factory=WorkerPool, init=False)

    @property
    def status(self) -> bool:
        with self._environment.read() as data:
            return data.status

    def mainloop(self) -> None:
        _logger.info('Starting...')

        self._setup()
        self._run()
        self._teardown()

    def _setup(self) -> None:
        _logger.info('Setting up...')

    def _run(self) -> None:
        assert self.endpoint is not None

        _logger.info('Handling messages...')

        while self.status:
            try:
                message = self._environment.receive_message(
                    self.endpoint,
                    timeout=self.message_queue_timeout,
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

    def _teardown(self) -> None:
        _logger.info('Tearing down...')
