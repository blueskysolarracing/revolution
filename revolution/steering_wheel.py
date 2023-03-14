from dataclasses import dataclass, field
from functools import partial
from logging import getLogger
from time import sleep
from typing import ClassVar, TypeAlias

from periphery import GPIO, SPI

from revolution.application import Application
from revolution.drivers import ADC78H89
from revolution.environment import Endpoint
from revolution.utilities import interpolate

_logger = getLogger(__name__)


@dataclass
class SteeringWheel(Application):
    """The class for steering wheel.

    Some features are not yet added and will be added in the later
    versions:
    - cruise mode
    """
    InputRange: ClassVar[TypeAlias] = tuple[float, float]
    Input: ClassVar[TypeAlias] = tuple[ADC78H89.InputChannel, InputRange]

    endpoint: ClassVar[Endpoint] = Endpoint.STEERING_WHEEL
    timeout: ClassVar[float] = 0.01
    acceleration_pedal_input_channel: ClassVar[ADC78H89.InputChannel] \
        = ADC78H89.InputChannel.AIN1  # TODO
    regeneration_pedal_input_channel: ClassVar[ADC78H89.InputChannel] \
        = ADC78H89.InputChannel.AIN2  # TODO
    acceleration_paddle_input_channel: ClassVar[ADC78H89.InputChannel] \
        = ADC78H89.InputChannel.AIN3  # TODO
    regeneration_paddle_input_channel: ClassVar[ADC78H89.InputChannel] \
        = ADC78H89.InputChannel.AIN4  # TODO
    thermistor_input_channel: ClassVar[ADC78H89.InputChannel] \
        = ADC78H89.InputChannel.AIN5  # TODO
    acceleration_pedal_input_range: ClassVar[InputRange] = 0, 1  # TODO
    regeneration_pedal_input_range: ClassVar[InputRange] = 0, 1  # TODO
    acceleration_paddle_input_range: ClassVar[InputRange] = 0, 1  # TODO
    regeneration_paddle_input_range: ClassVar[InputRange] = 0, 1  # TODO
    thermistor_input_range: ClassVar[InputRange] = 0, 1  # TODO
    conversions: ClassVar[dict[str, Input]] = {
        'acceleration_pedal_input': (
            acceleration_pedal_input_channel,
            acceleration_pedal_input_range,
        ),
        'regeneration_pedal_input': (
            regeneration_pedal_input_channel,
            regeneration_pedal_input_range,
        ),
        'acceleration_paddle_input': (
            acceleration_paddle_input_channel,
            acceleration_paddle_input_range,
        ),
        'regeneration_paddle_input': (
            regeneration_paddle_input_channel,
            regeneration_paddle_input_range,
        ),
        'thermistor_input': (
            thermistor_input_channel,
            thermistor_input_range,
        ),
    }

    converter_spi: SPI = field(default_factory=partial(SPI, '', 3, 1e6))

    # Motor
    direction_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    variable_field_magnet_up_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    variable_field_magnet_down_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO

    # Miscellaneous
    left_indicator_light_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    right_indicator_light_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    hazard_lights_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    daytime_running_lights_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    horn_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    fan_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO

    # Power
    array_relay_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    battery_relay_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO

    # Display
    backup_camera_control_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    steering_wheel_in_place_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    left_directional_pad_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    right_directional_pad_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    up_directional_pad_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    down_directional_pad_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    center_directional_pad_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO

    # Unclassified
    brake_pedal_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO

    converter: ADC78H89 = field(init=False)
    boolean_momentary_switch_gpios: dict[str, GPIO] = field(init=False)
    boolean_toggle_switch_gpios: dict[str, GPIO] = field(init=False)
    additive_toggle_switch_gpios: dict[str, GPIO] = field(init=False)

    def __post_init__(self) -> None:
        self.converter = ADC78H89(self.converter_spi)
        self.boolean_momentary_switch_gpios = {
            # Motor
            'direction_input': self.direction_switch_gpio,

            # Miscellaneous
            'left_indicator_light_status_input':
                self.left_indicator_light_switch_gpio,
            'right_indicator_light_status_input':
                self.right_indicator_light_switch_gpio,
            'hazard_lights_status_input': self.hazard_lights_switch_gpio,
            'horn_status_input': self.horn_switch_gpio,

            # Display
            'steering_wheel_in_place_status_input':
                self.steering_wheel_in_place_switch_gpio,
            'left_directional_pad_input':
                self.left_directional_pad_switch_gpio,
            'right_directional_pad_input':
                self.right_directional_pad_switch_gpio,
            'up_directional_pad_input': self.up_directional_pad_switch_gpio,
            'down_directional_pad_input':
                self.down_directional_pad_switch_gpio,
            'center_directional_pad_input':
                self.center_directional_pad_switch_gpio,

            # Unclassified
            'brake_status_input': self.brake_pedal_switch_gpio,
        }
        self.boolean_toggle_switch_gpios = {
            # Miscellaneous
            'daytime_running_lights_status_input':
                self.daytime_running_lights_switch_gpio,
            'fan_status_input': self.fan_switch_gpio,

            # Power
            'array_relay_status_input': self.array_relay_switch_gpio,
            'battery_relay_status_input': self.battery_relay_switch_gpio,

            # Display
            'backup_camera_control_status_input':
                self.backup_camera_control_switch_gpio,
        }
        self.additive_toggle_switch_gpios = {
            # Motor
            'variable_field_magnet_up_input':
                self.variable_field_magnet_up_switch_gpio,
            'variable_field_magnet_down_input':
                self.variable_field_magnet_down_switch_gpio,
        }

    def _setup(self) -> None:
        super()._setup()

        self._worker_pool.add(self.__update_converter)
        self._worker_pool.add(self.__update_momentary_switches)
        self._worker_pool.add(self.__update_toggle_switches)

    def __update_converter(self) -> None:
        while self._status:
            voltages = self.converter.voltages
            values = {}

            for (input_channel, (min_input, max_input)) \
                    in self.conversions.values():
                voltage = voltages[input_channel]
                values[input_channel] \
                    = interpolate(voltage, min_input, max_input, 0, 1)

            for attribute_name, (input_channel, _) in self.conversions.items():
                value = values[input_channel]

                with self.environment.write() as data:
                    setattr(data, attribute_name, value)

            sleep(self.timeout)

    def __update_momentary_switches(self) -> None:
        while self._status:
            for attribute_name, momentary_switch_gpio \
                    in self.boolean_momentary_switch_gpios.items():
                value = momentary_switch_gpio.read()

                with self.environment.write() as data:
                    setattr(data, attribute_name, value)

            sleep(self.timeout)

    def __update_toggle_switches(self) -> None:
        values = dict[GPIO, bool]()

        while self._status:
            for attribute_name, toggle_switch_gpio in \
                    self.boolean_toggle_switch_gpios.items():
                value = toggle_switch_gpio.read()

                if value and not values.get(toggle_switch_gpio, False):
                    with self.environment.read_and_write() as data:
                        setattr(
                            data,
                            attribute_name,
                            not getattr(data, attribute_name),
                        )

                values[toggle_switch_gpio] = value

            for attribute_name, toggle_switch_gpio \
                    in self.additive_toggle_switch_gpios.items():
                value = toggle_switch_gpio.read()

                if value and not values.get(toggle_switch_gpio, False):
                    with self.environment.read_and_write() as data:
                        setattr(
                            data,
                            attribute_name,
                            getattr(data, attribute_name) + 1,
                        )

                values[toggle_switch_gpio] = value

            sleep(self.timeout)
