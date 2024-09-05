from threading import Thread
from time import sleep
from typing import ClassVar
from unittest import TestCase, main

from door.threading2 import AcquirableDoor

from revolution.driver import Driver
from revolution.environment import Environment, Header, Message
from revolution.tests import configurations


class DriverTestCase(TestCase):
    TIMEOUT: ClassVar[float] = 1

    def test_array_relay_status(self) -> None:
        environment = Environment(
            AcquirableDoor(configurations.CONTEXTS),
            configurations.PERIPHERIES,
            configurations.SETTINGS,
        )
        driver_thread = Thread(target=Driver.main, args=(environment,))

        driver_thread.start()
        sleep(self.TIMEOUT)

        with environment.contexts() as contexts:
            self.assertFalse(contexts.power_array_relay_status_input)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0]

        sleep(self.TIMEOUT)

        with environment.contexts() as contexts:
            self.assertTrue(contexts.power_array_relay_status_input)

        environment.send_all(Message(Header.STOP))

        driver_thread.join()


if __name__ == '__main__':
    main()  # pragma: no cover
