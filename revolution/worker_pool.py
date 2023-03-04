from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Thread
from typing import Any


@dataclass
class WorkerPool:
    __threads: list[Thread] = field(default_factory=list, init=False)

    def add(
            self,
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
                except:  # noqa: E722
                    status = False

        thread = Thread(target=run)

        thread.start()
        self.__threads.append(thread)

    def join(self) -> None:
        for thread in self.__threads:
            thread.join()
