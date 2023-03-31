from dataclasses import dataclass, field
from logging import getLogger
from functools import partial
from time import sleep
from typing import ClassVar, TypeAlias
import threading

from periphery import SPI

from revolution.application import Application
from revolution.drivers import INA229
from revolution.environment import Endpoint

_logger = getLogger(__name__)


@dataclass
class PSM(Application):
    """
    The class for the Power Sense Module (PSM), responsible for measuring voltage and current for the battery, motor, array and low-voltage system.
    """
    endpoint: ClassVar[Endpoint] = Endpoint.PSM

    # PSM hardware constants
    """ The voltage may be stepped-down before feeding into the INA229"""
    battery_voltage_step_down_ratio: float = 2.0
    array_voltage_step_down_ratio:   float = 2.0
    motor_voltage_step_down_ratio:   float = 2.0
    lv_voltage_step_down_ratio:      float = 1.0

    battery_shunt_resistance_ohm:    float = 0.002
    array_shunt_resistance_ohm:      float = 0.002
    motor_shunt_resistance_ohm:      float = 0.002
    lv_shunt_resistance_ohm:         float = 0.010

    # SPI busses
    battery_psm_spi: SPI = field(default_factory=partial(SPI, '', 1, 2e6))
    array_psm_spi:   SPI = field(default_factory=partial(SPI, '', 1, 2e6))
    motor_psm_spi:   SPI = field(default_factory=partial(SPI, '', 1, 2e6))
    lv_psm_spi:      SPI = field(default_factory=partial(SPI, '', 1, 2e6))

    def __post_init__(self) -> None:
        self.battery_psm = INA229(self.battery_psm_spi, self.battery_voltage_step_down_ratio, self.battery_shunt_resistance_ohm)
        self.array_psm =   INA229(self.battery_psm_spi, self.array_voltage_step_down_ratio, self.array_shunt_resistance_ohm)
        self.motor_psm =   INA229(self.battery_psm_spi, self.motor_voltage_step_down_ratio, self.motor_shunt_resistance_ohm)
        self.lv_psm =      INA229(self.battery_psm_spi, self.lv_voltage_step_down_ratio, self.lv_shunt_resistance_ohm)

        self.battery_psm.ADC_range(INA229.ADC_range_enum.LOW_PRECISION)
        self.array_psm.ADC_range(INA229.ADC_range_enum.LOW_PRECISION)
        self.motor_psm.ADC_range(INA229.ADC_range_enum.LOW_PRECISION)
        self.lv_psm.ADC_range(INA229.ADC_range_enum.HIGH_PRECISION)

    def _setup(self) -> None:
        super()._setup()

        psm_run10ms = threading.Timer(interval=0.01, function=self._run_all_psms, name="psm_timer_10ms")

    def _run_all_psms(self) -> None:
        self.battery_psm.run10ms()
        setattr(self.environment.write(), "battery_voltage", self.battery_psm.voltage_filtered)
        setattr(self.environment.write(), "battery_current", self.battery_psm.current_filtered)

        self.array_psm.run10ms()
        setattr(self.environment.write(), "array_voltage", self.array_psm.voltage_filtered)
        setattr(self.environment.write(), "array_current", self.array_psm.current_filtered)

        self.motor_psm.run10ms()
        setattr(self.environment.write(), "motor_voltage", self.motor_psm.voltage_filtered)
        setattr(self.environment.write(), "motor_current", self.motor_psm.current_filtered)

        self.lv_psm.run10ms()
        setattr(self.environment.write(), "lv_voltage", self.lv_psm.voltage_filtered)
        setattr(self.environment.write(), "lv_current", self.lv_psm.current_filtered)
