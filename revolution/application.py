""":mod:`revolution.application` defines the abstract base class
:cls:`Application` from which all applications are inherited.
"""

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass, field
from logging import getLogger
from threading import Event
from typing import Any, ClassVar

from revolution.environment import Endpoint, Environment, Header
from revolution.worker_pool import WorkerPool

_logger = getLogger(__name__)


@dataclass
class Application(ABC):
    """The abstract base class for applications in ``revolution``."""

    @classmethod
    def main(cls, environment: Environment) -> None:
        """Launch the application with the supplied environment."""
        application = cls(environment)
        application.mainloop()

    endpoint: ClassVar[Endpoint]
    """The application endpoint."""
    environment: Environment
    """The application environment."""
    _handlers: dict[Header, Callable[..., Any]] \
        = field(default_factory=dict, init=False)
    _worker_pool: WorkerPool = field(default_factory=WorkerPool, init=False)
    __stoppage: Event = field(default_factory=Event, init=False)

    def mainloop(self) -> None:
        """Run the application.

        This is a blocking call. To stop an application, one must send a
        stop message to the application in a separate thread.

        :return: ``None``.
        """
        self._setup()
        self._run()
        self._teardown()

    @property
    def _status(self) -> bool:
        return not self.__stoppage.is_set()

    def _setup(self) -> None:
        self.__stoppage.clear()
        self._handlers[Header.STOP] = self.__handle_stop

    def _run(self) -> None:
        while self._status:
            message = self.environment.receive_message(self.endpoint)
            handler = self._handlers.get(message.header)

            if handler is None:
                _logger.error(f'Unable to handle message {message}')
            else:
                handler(*message.args, **message.kwargs)

    def _teardown(self) -> None:
        self._worker_pool.join()

    def __handle_stop(self) -> None:
        self.__stoppage.set()
