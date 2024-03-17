from collections.abc import Callable, Iterable, Mapping
from logging import getLogger
from threading import Thread
from typing import Any

_logger = getLogger(__name__)


class Worker(Thread):
    @staticmethod
    def wrap(function: Callable[..., object]) -> Callable[..., object]:
        def wrapper(*args: Any, **kwargs: Any) -> object:
            status = True
            result = None

            while status:
                status = False

                try:
                    result = function(*args, **kwargs)
                except:  # noqa: E722
                    _logger.exception('Exception raised during function call')

                    status = True

            return result

        return wrapper

    def __init__(
            self,
            group: None = None,
            target: Callable[..., object] | None = None,
            name: str | None = None,
            args: Iterable[Any] = (),
            kwargs: Mapping[str, Any] | None = None,
            *,
            daemon: bool | None = None,
    ) -> None:
        super().__init__(
            group,
            None if target is None else self.wrap(target),
            name,
            args,
            kwargs,
            daemon=daemon,
        )
