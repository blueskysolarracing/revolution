from math import inf
from time import sleep, time
from typing import Any, cast
from unittest import TestCase, main
from unittest.mock import DEFAULT, MagicMock, call

from revolution.drivers import ADC78H89, M2096, INA229
from revolution.environment import Direction


class ADC78H89TestCase(TestCase):
    def test_post_init(self) -> None:
        spi = MagicMock()
        spi.mode = 3
        spi.max_speed = 1e6
        spi.bit_order = 'msb'
        spi.bits_per_word = 8
        spi.extra_flags = 0

        ADC78H89(spi)

        spi.mode = 1

        self.assertRaises(ValueError, ADC78H89, spi)

        spi.mode = 3
        spi.max_speed = 0

        self.assertRaises(ValueError, ADC78H89, spi)

        spi.max_speed = inf

        self.assertRaises(ValueError, ADC78H89, spi)

        spi.max_speed = 1e6
        spi.bit_order = 'lsb'

        self.assertRaises(ValueError, ADC78H89, spi)

        spi.bit_order = 'msb'
        spi.bits_per_word = 7

        self.assertRaises(ValueError, ADC78H89, spi)

        spi.bits_per_word = 8
        spi.extra_flags = 1

        self.assertWarns(UserWarning, ADC78H89, spi)

    def test_voltages(self) -> None:
        spi = MagicMock()
        spi.mode = 3
        spi.max_speed = 1e6
        spi.bit_order = 'msb'
        spi.bits_per_word = 8
        spi.extra_flags = 0
        spi.transfer.side_effect = ([0, i] for i in range(8))
        converter = ADC78H89(spi)
        voltages = converter.voltages
        expected_voltages = {}

        for i, input_channel in enumerate(converter.InputChannel):
            expected_voltages[input_channel] \
                = converter.reference_voltage * i / converter.divisor

        self.assertDictEqual(voltages, expected_voltages)
        self.assertEqual(spi.transfer.call_count, 8)
        spi.transfer.assert_has_calls(
            (
                call([0b0001000, 0]),
                call([0b0010000, 0]),
                call([0b0011000, 0]),
                call([0b0100000, 0]),
                call([0b0101000, 0]),
                call([0b0110000, 0]),
                call([0b0111000, 0]),
                call([0b0000000, 0]),
            ),
        )


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


class ADC78H89TestCase(TestCase):
    def test_post_init(self) -> None:
        spi = MagicMock()
        spi.mode = 3
        spi.max_speed = 1e6
        spi.bit_order = 'msb'
        spi.bits_per_word = 8
        spi.extra_flags = 0

        INA229(spi)
    
    def test_conversion_times(self):
        self.assertEqual(self.voltage_conversion_time, 1052)
        self.assertEqual(self.current_conversion_time, 1052)
        self.assertEqual(self.temperature_conversion_time, 1052)

if __name__ == '__main__':
    main()
