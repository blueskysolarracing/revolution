from dataclasses import dataclass, field, fields
from functools import partial
from itertools import chain
from logging import getLogger
from periphery import GPIO, SPI
from time import sleep
from typing import ClassVar

from revolution.application import Application
from revolution.drivers import ADC78H89
from revolution.environment import Context, Endpoint

_logger = getLogger(__name__)


@dataclass
class SteeringWheel(Application):
    """The class for steering wheel.

    Some features are not yet added and will be added in the later
    versions:
    - cruise mode
    """

    endpoint: ClassVar[Endpoint] = Endpoint.STEERING_WHEEL
    timeout: ClassVar[float] = 0.01

    # Motor
    acceleration_pedal_input_channel: ClassVar[ADC78H89.InputChannel] \
        = ADC78H89.InputChannel.AIN1  # TODO
    regeneration_pedal_input_channel: ClassVar[ADC78H89.InputChannel] \
        = ADC78H89.InputChannel.AIN2  # TODO
    acceleration_paddle_input_channel: ClassVar[ADC78H89.InputChannel] \
        = ADC78H89.InputChannel.AIN3  # TODO
    regeneration_paddle_input_channel: ClassVar[ADC78H89.InputChannel] \
        = ADC78H89.InputChannel.AIN4  # TODO

    # Display
    thermistor_input_channel: ClassVar[ADC78H89.InputChannel] \
        = ADC78H89.InputChannel.AIN5  # TODO

    # Motor
    direction_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    variable_field_magnet_up_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    variable_field_magnet_down_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO

    # Miscellaneous
    left_indicator_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    right_indicator_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    hazard_lights_switch_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'in'))  # TODO
    daytime_running_light_switch_gpio: GPIO \
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

    adc78h89_spi: SPI = field(default_factory=partial(SPI, '', 3, 1e6))
    boolean_momentary_switch_gpios: dict[str, GPIO] = field(init=False)
    boolean_toggle_switch_gpios: dict[str, GPIO] = field(init=False)
    additive_toggle_switch_gpios: dict[str, GPIO] = field(init=False)
    adc78h89: ADC78H89 = field(init=False)

    def __post_init__(self) -> None:
        self.boolean_momentary_switch_gpios = {
            # Motor
            'direction_input': self.direction_switch_gpio,

            # Miscellaneous
            'left_indicator_status_input': self.left_indicator_switch_gpio,
            'right_indicator_status_input': self.right_indicator_switch_gpio,
            'hazard_lights_status_input': self.hazard_lights_switch_gpio,
            'horn_status_input': self.horn_switch_gpio,

            # Display
            'steering_wheel_in_place_status_input':
                self.steering_wheel_in_place_switch_gpio,
            'left_directional_pad_input': self.left_indicator_switch_gpio,
            'right_directional_pad_input': self.right_indicator_switch_gpio,
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
            'daytime_running_light_status_input':
                self.daytime_running_light_switch_gpio,
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
        self.adc78h89 = ADC78H89(self.adc78h89_spi)

        field_names = set[str]()
        attribute_names = set[str]()
        switch_gpios = set[GPIO]()

        for field_ in fields(Context):
            field_names.add(field_.name)

        for attribute_name, switch_gpio in chain(
                self.boolean_momentary_switch_gpios.items(),
                self.boolean_toggle_switch_gpios.items(),
                self.additive_toggle_switch_gpios.items(),
        ):
            if attribute_name in attribute_names:
                raise ValueError('duplicate attribute names')
            elif switch_gpio in switch_gpios:
                raise ValueError('duplicate switch gpios')
            elif attribute_name not in field_names:
                raise ValueError('unknown attribute name')

        for field_ in fields(self):
            if field_.type is GPIO:
                attribute = getattr(self, field_.name)

                if attribute not in switch_gpios:
                    raise ValueError('unclassified switch gpio')

    def _setup(self) -> None:
        super()._setup()

        self._worker_pool.add(self.__update_momentary_switches)
        self._worker_pool.add(self.__update_toggle_switches)
        self._worker_pool.add(self.__update_adc)

    def __update_momentary_switches(self) -> None:
        while self._status:
            for attribute_name, momentary_switch_gpio in \
                    self.boolean_momentary_switch_gpios.items():
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

            for attribute_name, toggle_switch_gpio in \
                    self.additive_toggle_switch_gpios.items():
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

    def __update_adc(self) -> None:
        while self._status:
            sleep(self.timeout)
