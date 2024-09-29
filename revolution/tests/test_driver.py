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

    def setUp(self) -> None:
        self.environment = Environment(
            AcquirableDoor(configurations.CONTEXTS),
            configurations.PERIPHERIES,
            configurations.SETTINGS,
        )
        self.driver_thread = Thread(target=Driver.main,
                                    args=(self.environment,))

        self.driver_thread.start()
        sleep(self.TIMEOUT)

    def tearDown(self) -> None:
        self.environment.send_all(Message(Header.STOP))
        self.driver_thread.join()

    def test_array_relay_status(self) -> None:
        with self.environment.contexts() as contexts:
            self.assertFalse(contexts.power_array_relay_status_input)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertTrue(contexts.power_array_relay_status_input)

    def test_motor_cruise_control_status(self) -> None:
        with self.environment.contexts() as contexts:
            self.assertFalse(contexts.motor_cruise_control_status_input)
        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0]

        sleep(self.TIMEOUT)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0xFF]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertTrue(contexts.motor_cruise_control_status_input)


if __name__ == '__main__':
    main()  # pragma: no cover
