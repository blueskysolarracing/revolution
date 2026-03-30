import time
from iclib.wavesculptor22 import StatusInformation
from struct import pack
from can import Message
from collections import deque

from dataclasses import replace
from threading import Thread
from time import sleep
from typing import ClassVar
from unittest import TestCase, main

from door.threading2 import AcquirableDoor
from pyexpat.errors import messages

from revolution import StatusesInformation
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

    def test_motor_controller_reset_timeout(self) -> None:
        self.reset_times = []  # Window For Reset
        intended_timeout = self.environment.settings.motor_reset_timeout
        test_duration = 5

        motor = self.environment.peripheries.motor_wavesculptor22
        original_reset = motor.reset

        def reset_function():
            self.reset_times.append(time.time())
            return original_reset()

        motor.reset = reset_function

        start = time.time()

        while time.time() - start <= test_duration:  # Continual Resets
            data = pack('<HHHBB', 0, 1, 1, 0, 0)

            msg = Message(
                arbitration_id=(
                        self.environment.peripheries.motor_wavesculptor22.motor_controller_base_address
                        + StatusInformation.MESSAGE_IDENTIFIER
                ),
                data=data,
                is_extended_id=False
            )

            motor.parse(msg)
            sleep(self.TIMEOUT)

        for i in range(1, len(self.reset_times)):
            self.assertGreaterEqual(self.reset_times[i] - self.reset_times[i - 1], intended_timeout)

    def test_motor_controller_reset_window(self) -> None:
        self.reset_window = deque()

        motor = self.environment.peripheries.motor_wavesculptor22
        original_reset = motor.reset

        def reset_function():
            now = time.time()
            self.reset_window.append(now)
            while self.reset_window and now - self.reset_window[0] > self.environment.settings.motor_reset_window:
                self.reset_window.popleft()
            return original_reset()

        motor.reset = reset_function

        limit = self.environment.settings.motor_reset_limit
        window = self.environment.settings.motor_reset_window

        start = time.time()

        while time.time() - start <= window * 2:
            data = pack('<HHHBB', 0, 1, 1, 0, 0)

            msg = Message(
                arbitration_id=(
                        motor.motor_controller_base_address
                        + StatusInformation.MESSAGE_IDENTIFIER
                ),
                data=data,
                is_extended_id=False
            )

            motor.parse(msg)
            sleep(self.TIMEOUT)

        self.assertLessEqual(len(self.reset_times), limit)

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
