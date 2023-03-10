from dataclasses import fields
from itertools import chain
from unittest import TestCase, main
from unittest.mock import MagicMock

from periphery import GPIO

from revolution.environment import Context, Environment
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

        for attribute_name in steering_wheel.conversions.keys():
            self.assertIn(attribute_name, field_names)

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


if __name__ == '__main__':
    main()
