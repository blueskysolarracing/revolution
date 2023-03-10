from math import inf
from time import sleep, time
from typing import Any, cast
from unittest import TestCase, main
from unittest.mock import DEFAULT, MagicMock, call

from revolution.drivers import M2096
from revolution.environment import Direction


class ADC78H89TestCase(TestCase):
    pass  # TODO


class M2096TestCase(TestCase):
    def test_post_init(self) -> None:
        controller = M2096(*(MagicMock() for _ in range(8)))
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
        cast(MagicMock, controller.main_switch_gpio).write.assert_called_with(
            False,
        )
        cast(MagicMock, controller.forward_or_reverse_switch_gpio) \
            .write \
            .assert_called_with(False)
        cast(MagicMock, controller.power_or_economical_switch_gpio) \
            .write \
            .assert_called_with(False)
        cast(MagicMock, controller.variable_field_magnet_up_switch_gpio) \
            .write \
            .assert_called_with(False)
        cast(MagicMock, controller.variable_field_magnet_down_switch_gpio) \
            .write \
            .assert_called_with(False)

    def test_revolution_period(self) -> None:
        def side_effect(*args: Any, **kwargs: Any) -> Any:
            sleep(timeout)

            return DEFAULT

        controller = M2096(*(MagicMock() for _ in range(8)))
        timeout = controller.revolution_timeout / 100
        cast(MagicMock, controller.revolution_gpio).poll.side_effect \
            = side_effect
        cast(MagicMock, controller.revolution_gpio).poll.return_value = True

        self.assertAlmostEqual(controller.revolution_period, 2 * timeout, 2)

        timeout = controller.revolution_timeout / 20

        self.assertAlmostEqual(controller.revolution_period, 2 * timeout, 2)

        cast(MagicMock, controller.revolution_gpio).poll.side_effect = None
        cast(MagicMock, controller.revolution_gpio).poll.return_value = False

        self.assertEqual(controller.revolution_period, inf)

    def test_status(self) -> None:
        controller = M2096(*(MagicMock() for _ in range(8)))
        cast(MagicMock, controller.main_switch_gpio).read.return_value = True

        self.assertTrue(controller.status)

        cast(MagicMock, controller.main_switch_gpio).read.return_value = False

        self.assertFalse(controller.status)

    def test_accelerate(self) -> None:
        controller = M2096(*(MagicMock() for _ in range(8)))
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
        controller = M2096(*(MagicMock() for _ in range(8)))
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
        controller = M2096(*(MagicMock() for _ in range(8)))
        cast(MagicMock, controller.main_switch_gpio).read.return_value = False
        timestamp = time()

        controller.state(True)
        self.assertGreaterEqual(
            time() - timestamp,
            controller.main_switch_timeout,
        )
        cast(MagicMock, controller.main_switch_gpio).write.assert_called_with(
            True,
        )

        cast(MagicMock, controller.main_switch_gpio).read.return_value = True
        timestamp = time()

        controller.state(False)
        self.assertLess(time() - timestamp, controller.main_switch_timeout)
        cast(MagicMock, controller.main_switch_gpio).write.assert_called_with(
            False,
        )

    def test_direct(self) -> None:
        controller = M2096(*(MagicMock() for _ in range(8)))

        controller.direct(Direction.FORWARD)
        cast(MagicMock, controller.forward_or_reverse_switch_gpio) \
            .write \
            .assert_called_with(False)
        controller.direct(Direction.BACKWARD)
        cast(MagicMock, controller.forward_or_reverse_switch_gpio) \
            .write \
            .assert_called_with(True)

    def test_economize(self) -> None:
        controller = M2096(*(MagicMock() for _ in range(8)))

        controller.economize(False)
        cast(MagicMock, controller.power_or_economical_switch_gpio) \
            .write \
            .assert_called_with(False)
        controller.economize(True)
        cast(MagicMock, controller.power_or_economical_switch_gpio) \
            .write \
            .assert_called_with(True)

    def test_variable_field_magnet_up(self) -> None:
        controller = M2096(*(MagicMock() for _ in range(8)))
        timestamp = time()

        controller.variable_field_magnet_up()
        self.assertGreaterEqual(
            time() - timestamp,
            controller.variable_field_magnet_switch_timeout,
        )
        cast(MagicMock, controller.variable_field_magnet_up_switch_gpio) \
            .write \
            .assert_has_calls((call(True), call(False)))

    def test_variable_field_magnet_down(self) -> None:
        controller = M2096(*(MagicMock() for _ in range(8)))
        timestamp = time()

        controller.variable_field_magnet_down()
        self.assertGreaterEqual(
            time() - timestamp,
            controller.variable_field_magnet_switch_timeout,
        )
        cast(MagicMock, controller.variable_field_magnet_down_switch_gpio) \
            .write \
            .assert_has_calls((call(True), call(False)))


if __name__ == '__main__':
    main()
