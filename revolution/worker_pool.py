from collections.abc import Callable
from dataclasses import dataclass, field
from logging import getLogger
from threading import Thread
from typing import Any

_logger = getLogger(__name__)


@dataclass
class WorkerPool:
    __threads: list[Thread] = field(default_factory=list, init=False)

    def add(
            self,
            exception_type: type[Exception],
            function: Callable[..., Any],
            /,
            *args: Any,
            **kwargs: Any,
    ) -> None:
        def run() -> None:
            status = False

            while not status:
                status = True

                try:
                    function(*args, **kwargs)
                except exception_type as exception:
                    _logger.exception(exception)

                    status = False

        thread = Thread(target=run)

        thread.start()
        self.__threads.append(thread)

    def join(self) -> None:
        for thread in self.__threads:
            thread.join()
