from collections import defaultdict
from dataclasses import fields
from itertools import chain
from threading import Thread
from time import sleep
from unittest import main, TestCase
from unittest.mock import MagicMock

from periphery import GPIO

from revolution.drivers import ADC78H89
from revolution.environment import Context, Environment, Header, Message
from revolution.steering_wheel import SteeringWheel


class SteeringWheelTestCase(TestCase):
    def test_post_init(self) -> None:
        context = Context()
        environment = Environment(context)
        spi = MagicMock()
        spi.mode = 3
        spi.max_speed = 1e6
        spi.bit_order = 'msb'
        spi.bits_per_word = 8
        spi.extra_flags = 0
        steering_wheel = SteeringWheel(
            environment,
            spi,
            *(MagicMock() for _ in range(19)),
        )
        field_names = set()

        for field in fields(Context):
            field_names.add(field.name)

        for attribute_name, (input_channel, input_range) \
                in steering_wheel.conversions.items():
            self.assertIn(attribute_name, field_names)
            self.assertNotAlmostEqual(*input_range)

        attribute_names = set[str]()
        switch_gpios = set[GPIO]()

        for attribute_name, switch_gpio in chain(
                steering_wheel.boolean_momentary_switch_gpios.items(),
                steering_wheel.boolean_toggle_switch_gpios.items(),
                steering_wheel.additive_toggle_switch_gpios.items(),
        ):
            self.assertNotIn(attribute_name, attribute_names)
            self.assertNotIn(switch_gpio, switch_gpios)
            self.assertIn(attribute_name, field_names)
            attribute_names.add(attribute_name)
            switch_gpios.add(switch_gpio)

        for field in fields(steering_wheel):
            if field.type is GPIO:
                attribute = getattr(steering_wheel, field.name)

                self.assertIn(attribute, switch_gpios)

    def test_update_converter(self) -> None:
        context = Context()
        environment = Environment(context)
        spi = MagicMock()
        spi.mode = 3
        spi.max_speed = 1e6
        spi.bit_order = 'msb'
        spi.bits_per_word = 8
        spi.extra_flags = 0
        converter = MagicMock()
        converter.voltages = defaultdict(int)
        converter.voltages[ADC78H89.InputChannel.GROUND] = 5
        steering_wheel = SteeringWheel(
            environment,
            spi,
            *(MagicMock() for _ in range(19)),
        )
        steering_wheel.converter = converter
        steering_wheel.conversions['debug'] \
            = ADC78H89.InputChannel.GROUND, (4, 6)
        thread = Thread(target=steering_wheel.mainloop)

        thread.start()
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertAlmostEqual(data.debug, 0.5)

        environment.send_message(steering_wheel.endpoint, Message(Header.STOP))
        thread.join()

    def test_update_momentary_switches(self) -> None:
        context = Context()
        environment = Environment(context)
        spi = MagicMock()
        spi.mode = 3
        spi.max_speed = 1e6
        spi.bit_order = 'msb'
        spi.bits_per_word = 8
        spi.extra_flags = 0
        converter = MagicMock()
        converter.voltages = defaultdict(int)
        gpio = MagicMock()
        gpio.read.return_value = False
        steering_wheel = SteeringWheel(
            environment,
            spi,
            *(MagicMock() for _ in range(19)),
        )
        steering_wheel.converter = converter
        steering_wheel.boolean_momentary_switch_gpios['debug'] = gpio
        thread = Thread(target=steering_wheel.mainloop)

        thread.start()
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertFalse(data.debug)

        gpio.read.return_value = True
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertTrue(data.debug)

        gpio.read.return_value = False
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertFalse(data.debug)

        environment.send_message(steering_wheel.endpoint, Message(Header.STOP))
        thread.join()

    def test_update_boolean_toggle_switches(self) -> None:
        context = Context()
        environment = Environment(context)
        spi = MagicMock()
        spi.mode = 3
        spi.max_speed = 1e6
        spi.bit_order = 'msb'
        spi.bits_per_word = 8
        spi.extra_flags = 0
        converter = MagicMock()
        converter.voltages = defaultdict(int)
        gpio = MagicMock()
        gpio.read.return_value = False
        steering_wheel = SteeringWheel(
            environment,
            spi,
            *(MagicMock() for _ in range(19)),
        )
        steering_wheel.converter = converter
        steering_wheel.boolean_toggle_switch_gpios['debug'] = gpio
        thread = Thread(target=steering_wheel.mainloop)

        thread.start()
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertFalse(data.debug)

        gpio.read.return_value = True
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertTrue(data.debug)

        gpio.read.return_value = False
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertTrue(data.debug)

        gpio.read.return_value = True
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertFalse(data.debug)

        gpio.read.return_value = False
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertFalse(data.debug)

        environment.send_message(steering_wheel.endpoint, Message(Header.STOP))
        thread.join()

    def test_update_additive_toggle_switches(self) -> None:
        context = Context(debug=0)
        environment = Environment(context)
        spi = MagicMock()
        spi.mode = 3
        spi.max_speed = 1e6
        spi.bit_order = 'msb'
        spi.bits_per_word = 8
        spi.extra_flags = 0
        converter = MagicMock()
        converter.voltages = defaultdict(int)
        gpio = MagicMock()
        gpio.read.return_value = False
        steering_wheel = SteeringWheel(
            environment,
            spi,
            *(MagicMock() for _ in range(19)),
        )
        steering_wheel.converter = converter
        steering_wheel.additive_toggle_switch_gpios['debug'] = gpio
        thread = Thread(target=steering_wheel.mainloop)

        thread.start()
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertEqual(data.debug, 0)

        gpio.read.return_value = True
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertEqual(data.debug, 1)

        gpio.read.return_value = False
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertEqual(data.debug, 1)

        gpio.read.return_value = True
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertEqual(data.debug, 2)

        gpio.read.return_value = False
        sleep(2 * steering_wheel.timeout)

        with environment.read() as data:
            self.assertEqual(data.debug, 2)

        environment.send_message(steering_wheel.endpoint, Message(Header.STOP))
        thread.join()


if __name__ == '__main__':
    main()
