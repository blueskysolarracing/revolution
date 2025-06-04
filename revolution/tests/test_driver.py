from dataclasses import replace
from threading import Thread
from time import sleep
from typing import ClassVar
from unittest import TestCase, main

from door.threading2 import AcquirableDoor

from revolution.driver import Driver
from revolution.environment import Environment, Header, Message
from revolution.tests import configurations


class DriverTestCase(TestCase):
    TIMEOUT: ClassVar[float] = 0.1

    def setUp(self) -> None:
        self.environment: Environment = Environment(
            AcquirableDoor(replace(configurations.CONTEXTS)),
            replace(configurations.PERIPHERIES),
            replace(configurations.SETTINGS),
        )
        self.driver_thread: Thread = Thread(
            target=Driver.main,
            args=(self.environment,),
        )

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
        ) = lambda *_: [0b01111111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertTrue(contexts.power_array_relay_status_input)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11111111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertFalse(contexts.power_array_relay_status_input)

    def test_motor_cruise_control_status(self) -> None:
        with self.environment.contexts() as contexts:
            self.assertFalse(contexts.motor_cruise_control_status_input)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11011111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertTrue(contexts.motor_cruise_control_status_input)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b00100000]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertTrue(contexts.motor_cruise_control_status_input)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11011111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertFalse(contexts.motor_cruise_control_status_input)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11111111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertFalse(contexts.motor_cruise_control_status_input)

    def test_left_light_status(self) -> None:
        with self.environment.contexts() as contexts:
            self.assertFalse(
                contexts.miscellaneous_left_indicator_light_status_input)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11111110]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertTrue(
                contexts.miscellaneous_left_indicator_light_status_input)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11111111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertFalse(
                contexts.miscellaneous_left_indicator_light_status_input)

    def test_right_light_status(self) -> None:
        with self.environment.contexts() as contexts:
            self.assertFalse(
                contexts.miscellaneous_right_indicator_light_status_input)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b01111111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertTrue(
                contexts.miscellaneous_right_indicator_light_status_input)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11111111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertFalse(
                contexts.miscellaneous_right_indicator_light_status_input)

    def test_motor_variable_field_magnet_up(self) -> None:
        with self.environment.contexts() as contexts:
            self.assertEqual(
                contexts.motor_variable_field_magnet_up_input, 0)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11111011]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertEqual(
                contexts.motor_variable_field_magnet_up_input, 1)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11111111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertEqual(
                contexts.motor_variable_field_magnet_up_input, 1)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11111011]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertEqual(
                contexts.motor_variable_field_magnet_up_input, 2)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11111111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertEqual(
                contexts.motor_variable_field_magnet_up_input, 2)

    def test_motor_variable_field_magnet_down(self) -> None:
        with self.environment.contexts() as contexts:
            self.assertEqual(
                contexts.motor_variable_field_magnet_down_input, 0)

        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11110111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertEqual(
                contexts.motor_variable_field_magnet_down_input, 1)
        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11111111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertEqual(
                contexts.motor_variable_field_magnet_down_input, 1)
        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11110111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertEqual(
                contexts.motor_variable_field_magnet_down_input, 2)
        (
            configurations  # type: ignore[method-assign]
            .STEERING_WHEEL_MCP23S17
            .read_register
        ) = lambda *_: [0b11111111]

        sleep(self.TIMEOUT)

        with self.environment.contexts() as contexts:
            self.assertEqual(
                contexts.motor_variable_field_magnet_down_input, 2)


if __name__ == '__main__':
    main()  # pragma: no cover
