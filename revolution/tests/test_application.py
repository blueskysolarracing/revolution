from dataclasses import dataclass
from threading import Thread
from time import sleep
from typing import Any, ClassVar
from unittest import TestCase, main

from revolution.application import Application
from revolution.environment import (
    Context,
    Endpoint,
    Environment,
    Header,
    Message,
)


@dataclass
class _Debugger(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.DEBUGGER
    mainloop_flag: bool = False
    setup_flag: bool = False
    teardown_flag: bool = False
    debug_flag: bool = False
    debug_args: tuple[Any, ...] | None = None
    debug_kwargs: dict[str, Any] | None = None

    def mainloop(self) -> None:
        super().mainloop()

        self.mainloop_flag = True

    def _setup(self) -> None:
        super()._setup()

        self._handlers[Header.DEBUG] = self.__handle_debug
        self.setup_flag = True

    def _teardown(self) -> None:
        self.teardown_flag = True

        super()._teardown()

    def __handle_debug(self, /, *args: Any, **kwargs: Any) -> None:
        self.debug_flag = True
        self.debug_args = args
        self.debug_kwargs = kwargs


class ApplicationTestCase(TestCase):
    def test_mainloop(self) -> None:
        context = Context()
        environment = Environment(context)
        debugger = _Debugger(environment)
        thread = Thread(target=debugger.mainloop)

        thread.start()
        thread.join(timeout=2 * debugger.message_queue_timeout)
        self.assertTrue(thread.is_alive())
        self.assertTrue(debugger.status)

        with environment.write() as data:
            data.status = False

        thread.join(timeout=2 * debugger.message_queue_timeout)
        self.assertFalse(thread.is_alive())
        self.assertFalse(debugger.status)
        self.assertTrue(debugger.mainloop_flag)
        self.assertTrue(debugger.setup_flag)
        self.assertTrue(debugger.teardown_flag)
        self.assertFalse(debugger.debug_flag)

    def test_run(self) -> None:
        context = Context()
        environment = Environment(context)
        debugger = _Debugger(environment)
        thread = Thread(target=debugger.mainloop)

        environment.send_message(
            Endpoint.DEBUGGER,
            Message(Header.DEBUG, (0, 1, 2), {'hello': 'world'}),
        )
        thread.start()
        sleep(debugger.message_queue_timeout)

        with environment.write() as data:
            data.status = False

        self.assertTrue(debugger.debug_flag)
        self.assertEqual(debugger.debug_args, (0, 1, 2))
        self.assertEqual(debugger.debug_kwargs, {'hello': 'world'})


if __name__ == '__main__':
    main()
