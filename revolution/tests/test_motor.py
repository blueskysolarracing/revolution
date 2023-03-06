from math import inf
from threading import Thread
from time import sleep, time
from typing import Any, cast
from unittest import TestCase, main
from unittest.mock import DEFAULT, MagicMock, call

from revolution.environment import (
    Context,
    Direction,
    Environment,
    Header,
    Message,
)
from revolution.motor import Motor, MotorController


class MotorControllerTestCase(TestCase):
    def test_post_init(self) -> None:
        controller = MotorController(*(MagicMock() for _ in range(8)))
        cast(MagicMock, controller.acceleration_potentiometer_spi) \
            .transfer \
            .return_value = [0, 0]
        cast(MagicMock, controller.regeneration_potentiometer_spi) \
            .transfer \
            .return_value = [0, 0]

        cast(MagicMock, controller.acceleration_potentiometer_spi) \
            .transfer \
            .assert_called_with([1 << 5, 0])
        cast(MagicMock, controller.regeneration_potentiometer_spi) \
            .transfer \
            .assert_called_with([1 << 5, 0])

    def test_revolution_period(self) -> None:
        def side_effect(*args: Any, **kwargs: Any) -> Any:
            sleep(timeout)

            return DEFAULT

        controller = MotorController(*(MagicMock() for _ in range(8)))
        timeout = controller.revolution_timeout / 100
        cast(MagicMock, controller.revolution_gpio).poll.side_effect \
            = side_effect
        cast(MagicMock, controller.revolution_gpio).poll.return_value \
            = True

        self.assertAlmostEqual(controller.revolution_period, timeout, 2)

        timeout = controller.revolution_timeout / 20

        self.assertAlmostEqual(controller.revolution_period, timeout, 2)

        cast(MagicMock, controller.revolution_gpio).poll.side_effect \
            = None
        cast(MagicMock, controller.revolution_gpio).poll.return_value \
            = False

        self.assertEqual(controller.revolution_period, inf)

    def test_status(self) -> None:
        controller = MotorController(*(MagicMock() for _ in range(8)))
        cast(MagicMock, controller.main_switch_gpio).read.return_value = False

        self.assertTrue(controller.status)

        cast(MagicMock, controller.main_switch_gpio).read.return_value = True

        self.assertFalse(controller.status)

    def test_accelerate(self) -> None:
        controller = MotorController(*(MagicMock() for _ in range(8)))
        cast(MagicMock, controller.acceleration_potentiometer_spi) \
            .transfer \
            .return_value = [0, 0]

        controller.accelerate(0)
        cast(MagicMock, controller.acceleration_potentiometer_spi) \
            .transfer \
            .assert_called_with([0, 0])
        controller.accelerate(0, True)
        cast(MagicMock, controller.acceleration_potentiometer_spi) \
            .transfer \
            .assert_called_with([1 << 5, 0])
        controller.accelerate(0.5)
        cast(MagicMock, controller.acceleration_potentiometer_spi) \
            .transfer \
            .assert_called_with([0, 1 << 7])
        controller.accelerate(0.5, True)
        cast(MagicMock, controller.acceleration_potentiometer_spi) \
            .transfer \
            .assert_called_with([1 << 5, 1 << 7])
        controller.accelerate(1)
        cast(MagicMock, controller.acceleration_potentiometer_spi) \
            .transfer \
            .assert_called_with([1, 0])
        controller.accelerate(1, True)
        cast(MagicMock, controller.acceleration_potentiometer_spi) \
            .transfer \
            .assert_called_with([1 << 5 | 1, 0])

    def test_regenerate(self) -> None:
        controller = MotorController(*(MagicMock() for _ in range(8)))
        cast(MagicMock, controller.regeneration_potentiometer_spi) \
            .transfer \
            .return_value = [0, 0]

        controller.regenerate(0)
        cast(MagicMock, controller.regeneration_potentiometer_spi) \
            .transfer \
            .assert_called_with([0, 0])
        controller.regenerate(0, True)
        cast(MagicMock, controller.regeneration_potentiometer_spi) \
            .transfer \
            .assert_called_with([1 << 5, 0])
        controller.regenerate(0.5)
        cast(MagicMock, controller.regeneration_potentiometer_spi) \
            .transfer \
            .assert_called_with([0, 1 << 7])
        controller.regenerate(0.5, True)
        cast(MagicMock, controller.regeneration_potentiometer_spi) \
            .transfer \
            .assert_called_with([1 << 5, 1 << 7])
        controller.regenerate(1)
        cast(MagicMock, controller.regeneration_potentiometer_spi) \
            .transfer \
            .assert_called_with([1, 0])
        controller.regenerate(1, True)
        cast(MagicMock, controller.regeneration_potentiometer_spi) \
            .transfer \
            .assert_called_with([1 << 5 | 1, 0])

    def test_state(self) -> None:
        controller = MotorController(*(MagicMock() for _ in range(8)))
        cast(MagicMock, controller.main_switch_gpio).read.return_value = True
        timestamp = time()

        controller.state(True)
        self.assertGreaterEqual(
            time() - timestamp,
            controller.main_switch_timeout,
        )
        cast(MagicMock, controller.main_switch_gpio) \
            .write \
            .assert_called_with(False)

        cast(MagicMock, controller.main_switch_gpio).read.return_value = False
        timestamp = time()

        controller.state(False)
        self.assertLess(time() - timestamp, controller.main_switch_timeout)
        cast(MagicMock, controller.main_switch_gpio) \
            .write \
            .assert_called_with(True)

    def test_direct(self) -> None:
        controller = MotorController(*(MagicMock() for _ in range(8)))

        controller.direct(Direction.FORWARD)
        cast(MagicMock, controller.forward_or_reverse_switch_gpio) \
            .write \
            .assert_called_with(False)
        controller.direct(Direction.BACKWARD)
        cast(MagicMock, controller.forward_or_reverse_switch_gpio) \
            .write \
            .assert_called_with(True)

        for direction in Direction:
            if direction != Direction.FORWARD \
                    and direction != Direction.BACKWARD:
                self.assertRaises(ValueError, controller.direct, direction)

    def test_economize(self) -> None:
        controller = MotorController(*(MagicMock() for _ in range(8)))

        controller.economize(False)
        cast(MagicMock, controller.power_or_economical_switch_gpio) \
            .write \
            .assert_called_with(False)
        controller.economize(True)
        cast(MagicMock, controller.power_or_economical_switch_gpio) \
            .write \
            .assert_called_with(True)

    def test_gear_up(self) -> None:
        controller = MotorController(*(MagicMock() for _ in range(8)))
        timestamp = time()

        controller.gear_up()
        self.assertGreaterEqual(
            time() - timestamp,
            controller.vfm_switch_timeout,
        )
        cast(MagicMock, controller.vfm_up_switch_gpio) \
            .write \
            .assert_has_calls((call(True), call(False)))

    def test_gear_down(self) -> None:
        controller = MotorController(*(MagicMock() for _ in range(8)))
        timestamp = time()

        controller.gear_down()
        self.assertGreaterEqual(
            time() - timestamp,
            controller.vfm_switch_timeout,
        )
        cast(MagicMock, controller.vfm_down_switch_gpio) \
            .write \
            .assert_has_calls((call(True), call(False)))


class MotorTestCase(TestCase):
    def test_update_status(self) -> None:
        context = Context()
        environment = Environment(context)
        motor = Motor(environment, MagicMock())
        thread = Thread(target=motor.mainloop)

        thread.start()
        sleep(1)
        cast(MagicMock, motor.controller).state.assert_called_with(False)

        with environment.write() as data:
            data.motor_status_input = True

        sleep(1)
        cast(MagicMock, motor.controller).state.assert_called_with(True)
        environment.send_message(motor.endpoint, Message(Header.STOP))
        thread.join()

    def test_update_spi(self) -> None:
        context = Context()
        environment = Environment(context)
        motor = Motor(environment, MagicMock())
        thread = Thread(target=motor.mainloop)

        thread.start()

        with environment.write() as data:
            data.motor_acceleration_input = 1
            data.motor_regeneration_input = 1
            data.brake_status_input = 1

        sleep(1)
        cast(MagicMock, motor.controller).accelerate.assert_not_called()
        cast(MagicMock, motor.controller).regenerate.assert_not_called()

        with environment.write() as data:
            data.motor_status_input = True

        sleep(1)
        self.assertRaises(
            AssertionError,
            cast(MagicMock, motor.controller).accelerate.assert_any_call,
            1,
        )
        self.assertRaises(
            AssertionError,
            cast(MagicMock, motor.controller).regenerate.assert_any_call,
            1,
        )
        cast(MagicMock, motor.controller).accelerate.assert_called_with(0)
        cast(MagicMock, motor.controller).regenerate.assert_called_with(0)

        with environment.write() as data:
            data.brake_status_input = 0

        sleep(1)
        self.assertRaises(
            AssertionError,
            cast(MagicMock, motor.controller).accelerate.assert_any_call,
            1,
        )
        cast(MagicMock, motor.controller).accelerate.assert_called_with(0)
        cast(MagicMock, motor.controller).regenerate.assert_called_with(1)

        with environment.write() as data:
            data.motor_regeneration_input = 0

        sleep(1)
        cast(MagicMock, motor.controller).accelerate.assert_called_with(1)
        cast(MagicMock, motor.controller).regenerate.assert_called_with(0)
        environment.send_message(motor.endpoint, Message(Header.STOP))
        thread.join()

    def test_update_gpio(self) -> None:
        context = Context()
        environment = Environment(context)
        motor = Motor(environment, MagicMock())
        thread = Thread(target=motor.mainloop)

        thread.start()
        sleep(1)
        self.assertRaises(
            AssertionError,
            cast(MagicMock, motor.controller).direct.assert_any_call,
            Direction.BACKWARD,
        )
        self.assertRaises(
            AssertionError,
            cast(MagicMock, motor.controller).economize.assert_any_call,
            False,
        )
        cast(MagicMock, motor.controller).direct.assert_called_with(
            Direction.FORWARD,
        )
        cast(MagicMock, motor.controller).economize.assert_called_with(True)

        with environment.write() as data:
            data.motor_directional_input = Direction.BACKWARD
            data.motor_economical_mode_input = False

        sleep(1)
        cast(MagicMock, motor.controller).direct.assert_called_with(
            Direction.BACKWARD,
        )
        cast(MagicMock, motor.controller).economize.assert_called_with(False)
        environment.send_message(motor.endpoint, Message(Header.STOP))
        thread.join()

    def test_update_gear(self) -> None:
        context = Context()
        environment = Environment(context)
        motor = Motor(environment, MagicMock())
        thread = Thread(target=motor.mainloop)

        thread.start()
        sleep(1)
        cast(MagicMock, motor.controller).gear_up.assert_not_called()
        cast(MagicMock, motor.controller).gear_down.assert_not_called()

        with environment.write() as data:
            data.motor_gear_input = 3

        sleep(1)
        self.assertEqual(
            cast(MagicMock, motor.controller).gear_up.call_count,
            3,
        )
        cast(MagicMock, motor.controller).gear_down.assert_not_called()
        cast(MagicMock, motor.controller).gear_up.reset_mock()
        cast(MagicMock, motor.controller).gear_down.reset_mock()

        with environment.read_and_write() as data:
            self.assertEqual(data.motor_gear_input, 0)
            data.motor_gear_input = -3

        sleep(1)
        cast(MagicMock, motor.controller).gear_up.assert_not_called()
        self.assertEqual(
            cast(MagicMock, motor.controller).gear_down.call_count,
            3,
        )
        cast(MagicMock, motor.controller).gear_up.reset_mock()
        cast(MagicMock, motor.controller).gear_down.reset_mock()

        with environment.read() as data:
            self.assertEqual(data.motor_gear_input, 0)

        sleep(1)
        cast(MagicMock, motor.controller).gear_up.assert_not_called()
        cast(MagicMock, motor.controller).gear_down.assert_not_called()
        environment.send_message(motor.endpoint, Message(Header.STOP))
        thread.join()

    def test_update_revolution(self) -> None:
        context = Context()
        environment = Environment(context)
        motor = Motor(environment, MagicMock())
        motor.controller.revolution_period = inf
        thread = Thread(target=motor.mainloop)

        thread.start()
        sleep(1)

        with environment.read() as data:
            self.assertEqual(data.motor_revolution_period, inf)

        motor.controller.revolution_period = 1

        sleep(1)

        with environment.read() as data:
            self.assertEqual(data.motor_revolution_period, 1)

        environment.send_message(motor.endpoint, Message(Header.STOP))
        thread.join()


if __name__ == '__main__':
    main()
