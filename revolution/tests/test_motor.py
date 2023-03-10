from math import inf
from threading import Thread
from time import sleep
from unittest import TestCase, main
from unittest.mock import MagicMock

from revolution.environment import (
    Context,
    Direction,
    Environment,
    Header,
    Message,
)
from revolution import Motor


class MotorTestCase(TestCase):
    def test_update_status(self) -> None:
        context = Context()
        environment = Environment(context)
        controller = MagicMock()
        motor = Motor(environment, *(MagicMock() for _ in range(8)))
        motor.controller = controller
        thread = Thread(target=motor.mainloop)

        thread.start()
        sleep(2 * motor.timeout)
        controller.state.assert_called_with(False)

        with environment.write() as data:
            data.motor_status_input = True

        sleep(2 * motor.timeout)
        controller.state.assert_called_with(True)
        environment.send_message(motor.endpoint, Message(Header.STOP))
        thread.join()

    def test_update_spi(self) -> None:
        context = Context()
        environment = Environment(context)
        controller = MagicMock()
        motor = Motor(environment, *(MagicMock() for _ in range(8)))
        motor.controller = controller
        thread = Thread(target=motor.mainloop)

        thread.start()

        with environment.write() as data:
            data.acceleration_input = 1
            data.regeneration_input = 1
            data.brake_status_input = True

        sleep(2 * motor.timeout)
        controller.accelerate.assert_not_called()
        controller.regenerate.assert_not_called()

        with environment.write() as data:
            data.motor_status_input = True

        sleep(2 * motor.timeout)
        self.assertRaises(
            AssertionError,
            controller.accelerate.assert_any_call,
            1,
        )
        self.assertRaises(
            AssertionError,
            controller.regenerate.assert_any_call,
            1,
        )
        controller.accelerate.assert_called_with(0)
        controller.regenerate.assert_called_with(0)

        with environment.write() as data:
            data.brake_status_input = False

        sleep(2 * motor.timeout)
        self.assertRaises(
            AssertionError,
            controller.accelerate.assert_any_call,
            1,
        )
        controller.accelerate.assert_called_with(0)
        controller.regenerate.assert_called_with(1)

        with environment.write() as data:
            data.regeneration_input = 0

        sleep(2 * motor.timeout)
        controller.accelerate.assert_called_with(1)
        controller.regenerate.assert_called_with(0)
        environment.send_message(motor.endpoint, Message(Header.STOP))
        thread.join()

    def test_update_gpio(self) -> None:
        context = Context()
        environment = Environment(context)
        controller = MagicMock()
        motor = Motor(environment, *(MagicMock() for _ in range(8)))
        motor.controller = controller
        thread = Thread(target=motor.mainloop)

        thread.start()
        sleep(2 * motor.timeout)
        self.assertRaises(
            AssertionError,
            controller.direct.assert_any_call,
            Direction.BACKWARD,
        )
        self.assertRaises(
            AssertionError,
            controller.economize.assert_any_call,
            False,
        )
        controller.direct.assert_called_with(Direction.FORWARD)
        controller.economize.assert_called_with(True)

        with environment.write() as data:
            data.direction_input = Direction.BACKWARD
            data.economical_mode_input = False

        sleep(2 * motor.timeout)
        controller.direct.assert_called_with(Direction.BACKWARD)
        controller.economize.assert_called_with(False)
        environment.send_message(motor.endpoint, Message(Header.STOP))
        thread.join()

    def test_update_variable_field_magnet(self) -> None:
        context = Context()
        environment = Environment(context)
        controller = MagicMock()
        motor = Motor(environment, *(MagicMock() for _ in range(8)))
        motor.controller = controller
        thread = Thread(target=motor.mainloop)

        thread.start()
        sleep(2 * motor.timeout)
        controller.variable_field_magnet_up.assert_not_called()
        controller.variable_field_magnet_down.assert_not_called()

        with environment.write() as data:
            data.variable_field_magnet_up_input = 3

        sleep(4 * motor.timeout)
        self.assertEqual(controller.variable_field_magnet_up.call_count, 3)
        controller.variable_field_magnet_down.assert_not_called()
        controller.variable_field_magnet_up.reset_mock()
        controller.variable_field_magnet_down.reset_mock()

        with environment.read_and_write() as data:
            self.assertEqual(data.variable_field_magnet_up_input, 0)
            data.variable_field_magnet_down_input = 3

        sleep(4 * motor.timeout)
        controller.variable_field_magnet_up.assert_not_called()
        self.assertEqual(controller.variable_field_magnet_down.call_count, 3)
        controller.variable_field_magnet_up.reset_mock()
        controller.variable_field_magnet_down.reset_mock()

        with environment.read() as data:
            self.assertEqual(data.variable_field_magnet_down_input, 0)

        sleep(2 * motor.timeout)
        controller.variable_field_magnet_up.assert_not_called()
        controller.variable_field_magnet_down.assert_not_called()

        with environment.write() as data:
            data.variable_field_magnet_up_input = 3
            data.variable_field_magnet_down_input = 3

        sleep(2 * motor.timeout)
        controller.variable_field_magnet_up.assert_not_called()
        controller.variable_field_magnet_down.assert_not_called()
        environment.send_message(motor.endpoint, Message(Header.STOP))
        thread.join()

    def test_update_revolution(self) -> None:
        context = Context()
        environment = Environment(context)
        controller = MagicMock()
        motor = Motor(environment, *(MagicMock() for _ in range(8)))
        motor.controller = controller
        controller.revolution_period = inf
        thread = Thread(target=motor.mainloop)

        thread.start()
        sleep(2 * motor.timeout)

        with environment.read() as data:
            self.assertEqual(data.revolution_period, inf)

        controller.revolution_period = 1

        sleep(2 * motor.timeout)

        with environment.read() as data:
            self.assertEqual(data.revolution_period, 1)

        environment.send_message(motor.endpoint, Message(Header.STOP))
        thread.join()


if __name__ == '__main__':
    main()
