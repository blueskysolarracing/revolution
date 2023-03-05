from dataclasses import dataclass, field
from threading import Thread
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
    mainloop_flag: bool = field(default=False, init=False)
    setup_flag: bool = field(default=False, init=False)
    run_flag: bool = field(default=False, init=False)
    teardown_flag: bool = field(default=False, init=False)
    debug_flag: bool = field(default=False, init=False)
    debug_args: tuple[Any, ...] = field(default=(), init=False)
    debug_kwargs: dict[str, Any] = field(default_factory=dict, init=False)

    def mainloop(self) -> None:
        super().mainloop()

        self.mainloop_flag = True

    def _setup(self) -> None:
        super()._setup()

        self._handlers[Header.DEBUG] = self.__handle_debug
        self.setup_flag = True

    def _run(self) -> None:
        super()._run()

        self.run_flag = True

    def _teardown(self) -> None:
        self.teardown_flag = True

        super()._teardown()

    def __handle_debug(self, /, *args: Any, **kwargs: Any) -> None:
        self.debug_flag = True
        self.debug_args += args
        self.debug_kwargs |= kwargs


class ApplicationTestCase(TestCase):
    def test_mainloop(self) -> None:
        context = Context()
        environment = Environment(context)
        debugger = _Debugger(environment)
        thread = Thread(target=debugger.mainloop)

        self.assertFalse(debugger.mainloop_flag)
        self.assertFalse(debugger.setup_flag)
        self.assertFalse(debugger.run_flag)
        self.assertFalse(debugger.teardown_flag)
        self.assertFalse(debugger.debug_flag)
        thread.start()
        environment.send_message(debugger.endpoint, Message(Header.STOP))
        thread.join()
        self.assertTrue(debugger.mainloop_flag)
        self.assertTrue(debugger.setup_flag)
        self.assertTrue(debugger.run_flag)
        self.assertTrue(debugger.teardown_flag)
        self.assertFalse(debugger.debug_flag)

    def test_run(self) -> None:
        context = Context()
        environment = Environment(context)
        debugger = _Debugger(environment)
        thread = Thread(target=debugger.mainloop)

        self.assertFalse(debugger.debug_flag)
        self.assertSequenceEqual(debugger.debug_args, ())
        self.assertDictEqual(debugger.debug_kwargs, {})
        thread.start()
        environment.send_message(
            debugger.endpoint,
            Message(Header.DEBUG, (0, 1), {'hello': 'world'}),
        )
        environment.send_message(
            debugger.endpoint,
            Message(Header.DEBUG, (2,)),
        )
        environment.send_message(debugger.endpoint, Message(Header.STOP))
        thread.join()
        self.assertTrue(debugger.debug_flag)
        self.assertSequenceEqual(debugger.debug_args, (0, 1, 2))
        self.assertDictEqual(debugger.debug_kwargs, {'hello': 'world'})


if __name__ == '__main__':
    main()
