from dataclasses import dataclass, field
from functools import partial
from logging import getLogger
from time import sleep
from typing import ClassVar, TypeAlias

from periphery import GPIO

from revolution.application import Application
from revolution.environment import Endpoint
from revolution.drivers import RelayController

@dataclass
class Relay(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.RELAY
    
    battery_relay_high_side_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    battery_relay_low_side_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    battery_relay_precharge_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    
    array_relay_high_side_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    array_relay_low_side_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    array_relay_precharge_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    
    def __post_init__(self) -> None:
        # TODO: initialize two RelayControllers, one for battery, one for array
        pass

    def _setup(self) -> None:
        super()._setup()
        # TODO: create thread which opens and closes relays based on readings from the environment

