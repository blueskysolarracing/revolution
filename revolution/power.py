from dataclasses import dataclass, field
from functools import partial
from logging import getLogger
from time import sleep
from typing import ClassVar, TypeAlias

from periphery import GPIO

from revolution.application import Application
from revolution.environment import Endpoint
from revolution.drivers import (
    RelayController,
    MaximumPowerPointTrackersController,
    HighVoltageDischargeController,
    SafeStateController
)

@dataclass
class Power(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.POWER
    
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
    
    high_voltage_discharge_control_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    
    safe_state_trigger_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO
    
    maximum_power_point_trackers_12v_enable_gpio: GPIO \
        = field(default_factory=partial(GPIO, '', 0, 'out'))  # TODO    
    
    def __post_init__(self) -> None:
        self.battery_relay = RelayController(
            high_side_gpio=self.battery_relay_high_side_gpio,
            low_side_gpio=self.battery_relay_low_side_gpio,
            precharge_gpio=self.battery_relay_precharge_gpio
        )
        self.array_relay = RelayController(
            high_side_gpio=self.array_relay_high_side_gpio,
            low_side_gpio=self.array_relay_low_side_gpio,
            precharge_gpio=self.array_relay_precharge_gpio
        )
        self.mppts = MaximumPowerPointTrackersController(
            mppts_12v_enable_gpio=self.maximum_power_point_trackers_12v_enable_gpio
        )
        self.hv_discharge = HighVoltageDischargeController(
            high_voltage_discharge_control_gpio=self.high_voltage_discharge_control_gpio
        )
        self.safe_state = SafeStateController(
            safe_state_trigger_gpio=self.safe_state_trigger_gpio
        )



    def _setup(self) -> None:
        super()._setup()
        self._worker_pool.add(self.__array_side_routine)
        self._worker_pool.add(self.__battery_side_routine)
        self._worker_pool.add(self.__safe_state_routine)

    
    def __array_side_routine(self) -> None:
        pass

    def __battery_side_routine(self) -> None:
        pass

    def __safe_state_routine(self) -> None:
        pass
