from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass, field
from logging import getLogger
from threading import Event
from typing import Any, ClassVar

from revolution.environment import Endpoint, Environment, Header

_logger = getLogger(__name__)


@dataclass
class Application(ABC):
    @classmethod
    def main(cls, environment: Environment) -> None:
        application = cls(environment)

        application.mainloop()

    endpoint: ClassVar[Endpoint]
    environment: Environment
    _handlers: dict[Header, Callable[..., Any]] = field(
        default_factory=dict,
        init=False,
    )
    _stoppage: Event = field(default_factory=Event, init=False)

    def mainloop(self) -> None:
        self._setup()
        self._run()
        self._teardown()

    def _setup(self) -> None:
        self._handlers[Header.STOP] = self._handle_stop

        self._stoppage.clear()

    def _run(self) -> None:
        while not self._stoppage.is_set():
            message = self.environment.receive(self.endpoint)
            handler = self._handlers.get(message.header)

            if handler is None:
                _logger.error(f'Unable to handle message {repr(message)}')
            else:
                try:
                    handler(*message.args, **message.kwargs)
                except:  # noqa: E722
                    _logger.exception('Exception raised during handler call')

    def _teardown(self) -> None:
        pass

    def _handle_stop(self) -> None:
        self._stoppage.set()
