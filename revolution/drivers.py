from dataclasses import dataclass
from enum import IntEnum
from logging import getLogger
from math import inf
from time import sleep, time
from typing import ClassVar
from warnings import warn
from bidict import bidict
import collections

from periphery import GPIO, SPI

from revolution.environment import Direction

_logger = getLogger(__name__)


@dataclass
class M2096:
    @staticmethod
    def __position_potentiometer(
            spi: SPI,
            position: float,
            eeprom: bool,
    ) -> None:
        if not 0 <= position <= 1:
            raise ValueError('position not between 0 and 1')

        raw_data = round(256 * position)

        if eeprom:
            raw_data |= 1 << 13

        data = [raw_data >> 8, raw_data & ((1 << 8) - 1)]

        spi.transfer(data)

    main_switch_timeout: ClassVar[float] = 5
    variable_field_magnet_switch_timeout: ClassVar[float] = 0.2
    revolution_timeout: ClassVar[float] = 5
    acceleration_potentiometer_spi: SPI
    regeneration_potentiometer_spi: SPI
    main_switch_gpio: GPIO
    forward_or_reverse_switch_gpio: GPIO
    power_or_economical_switch_gpio: GPIO
    variable_field_magnet_up_switch_gpio: GPIO
    variable_field_magnet_down_switch_gpio: GPIO
    revolution_gpio: GPIO

    def __post_init__(self) -> None:
        self.accelerate(0, True)
        self.regenerate(0, True)
        self.main_switch_gpio.write(False)
        self.forward_or_reverse_switch_gpio.write(False)
        self.power_or_economical_switch_gpio.write(False)
        self.variable_field_magnet_up_switch_gpio.write(False)
        self.variable_field_magnet_down_switch_gpio.write(False)

    @property
    def revolution_period(self) -> float:
        if not self.revolution_gpio.poll(self.revolution_timeout):
            return inf

        timestamp = time()

        if not self.revolution_gpio.poll(self.revolution_timeout):
            return inf

        return 2 * (time() - timestamp)

    @property
    def status(self) -> bool:
        return self.main_switch_gpio.read()

    def accelerate(self, acceleration: float, eeprom: bool = False) -> None:
        self.__position_potentiometer(
            self.acceleration_potentiometer_spi,
            acceleration,
            eeprom,
        )

    def regenerate(self, regeneration: float, eeprom: bool = False) -> None:
        self.__position_potentiometer(
            self.regeneration_potentiometer_spi,
            regeneration,
            eeprom,
        )

    def state(self, status: bool) -> None:
        wait = status and not self.status

        self.main_switch_gpio.write(status)

        if wait:
            sleep(self.main_switch_timeout)

    def direct(self, direction: Direction) -> None:
        self.forward_or_reverse_switch_gpio.write(bool(direction))

    def economize(self, mode: bool) -> None:
        self.power_or_economical_switch_gpio.write(mode)

    def variable_field_magnet_up(self) -> None:
        self.variable_field_magnet_up_switch_gpio.write(True)
        sleep(self.variable_field_magnet_switch_timeout)
        self.variable_field_magnet_up_switch_gpio.write(False)

    def variable_field_magnet_down(self) -> None:
        self.variable_field_magnet_down_switch_gpio.write(True)
        sleep(self.variable_field_magnet_switch_timeout)
        self.variable_field_magnet_down_switch_gpio.write(False)


@dataclass
class ADC78H89:
    """The wrapper class for Texas Instruments ADC78H89 7-Channel, 500
    KSPS, 12-Bit A/D Converter.

    Datasheet for this device is included in the documentation of
    ``revolution``.

    Summary of specifications:
    - Maximum conversion rate is 500 KSPS.
    - Data is straight binary, refer to Fig. 23.
    - Each conversion requires 16 CLK cycle, and is triggered when !CS
      goes low. The conversion is applied to the channel in the Control
      Register. Therefore, there is a one sample delay between writing
      to the control register and reading the data.
    - Write to the Control Register to select which channel is being
      sampled: [X X ADD2 ADD1 ADD0 X X X].
    - Even though this register is 8 bytes, writing to it requires 16
      clock cycles since a conversion is taking place in parallel. Only
      the first 8 bytes are read.
    - First conversion after power-up is for Channel #1 (0x00).
    """

    class InputChannel(IntEnum):
        """The enum class for input channels."""

        AIN1: int = 0
        """The first (default) input channel."""
        AIN2: int = 1
        """The second input channel."""
        AIN3: int = 2
        """The third input channel."""
        AIN4: int = 3
        """The fourth input channel."""
        AIN5: int = 4
        """The fifth input channel."""
        AIN6: int = 5
        """The fifth input channel."""
        AIN7: int = 6
        """The seventh input channel."""
        GROUND: int = 7
        """The ground input channel."""

    spi_mode: ClassVar[int] = 3
    """The supported spi mode."""
    min_spi_max_speed: ClassVar[float] = 5e5
    """The supported minimum spi maximum speed."""
    max_spi_max_speed: ClassVar[float] = 8e6
    """The supported maximum spi maximum speed."""
    spi_bit_order: ClassVar[str] = 'msb'
    """The supported spi bit order."""
    spi_word_bit_count: ClassVar[int] = 8
    """The supported spi number of bits per word."""
    offset: ClassVar[int] = 3
    """The input channel bit offset for control register bits."""
    reference_voltage: ClassVar[float] = 3.3
    """The reference voltage value (in volts)."""
    divisor: ClassVar[float] = 4096
    """The lsb width for ADC78H89."""
    spi: SPI
    """The SPI for the ADC device."""

    def __post_init__(self) -> None:
        if self.spi.mode != self.spi_mode:
            raise ValueError('unsupported spi mode')
        elif not self.min_spi_max_speed <= self.spi.max_speed \
                <= self.max_spi_max_speed:
            raise ValueError('unsupported spi maximum speed')
        elif self.spi.bit_order != self.spi_bit_order:
            raise ValueError('unsupported spi bit order')
        elif self.spi.bits_per_word != self.spi_word_bit_count:
            raise ValueError('unsupported spi number of bits per word')

        if self.spi.extra_flags:
            warn('unknown spi extra flags')

    @property
    def voltages(self) -> dict[InputChannel, float]:
        """Handle the SPI calls and return the last unfiltered voltage
        for the specified input channel.

        :param input_channel: The input channel to query.
        :return: The last unfiltered voltage for the specified input
                 channel.
        """
        voltages = {}

        for input_channel in self.InputChannel:
            next_input_channel = (input_channel + 1) % len(self.InputChannel)
            sent_data = [(next_input_channel << self.offset), 0]
            received_data = self.spi.transfer(sent_data)

            assert len(received_data) == 2

            raw_data = received_data[0] << self.spi_word_bit_count \
                | received_data[1]
            voltages[input_channel] \
                = self.reference_voltage * raw_data / self.divisor

        return voltages


@dataclass
class INA229:
    """
    The wrapper class for Texas Instruments INA229 20-Bit ADC. Used to accurately measure HV and LV power.

    Datasheet for this device is included in the documentation of
    ``revolution``.

    Summary of specifications:
    -Max. input voltage: 85V, max. shunt voltage: +-163.84mV
    -Max. SPI clock: 10MHz, SPI mode 1
    -Integrated temperature sensor
    -Can fire alert interrupts with dedicated signal
    -Configurable parameters
        -Full scale range of shunt voltage (±40.96mv or ±163.84mV)
        -ADC conversion period (50us to 4120us)
        -Number of averages (1 to 1024)
        -External shunt calibrated resistance
    """
    
    _register_map = {
        # name      :       [addr,         size (B), read/write,        data]
        "CONFIG":           {"addr":0x00, "size":2, "permission":"RW", "data":0x0000},
        "ADC_CONFIG":       {"addr":0x01, "size":2, "permission":"RW", "data":0xFB68},
        "SHUNT_CAL":        {"addr":0x02, "size":2, "permission":"RW", "data":0x1000},
        "SHUNT_TEMPCO":     {"addr":0x03, "size":2, "permission":"RW", "data":0x0000},
        "VSHUNT":           {"addr":0x04, "size":3, "permission":"RO", "data":0x000000},
        "VBUS":             {"addr":0x05, "size":3, "permission":"RO", "data":0x000000},
        "DIETEMP":          {"addr":0x06, "size":2, "permission":"RO", "data":0x0000},
        "CURRENT":          {"addr":0x07, "size":3, "permission":"RO", "data":0x000000},
        "POWER":            {"addr":0x08, "size":3, "permission":"RO", "data":0x000000},
        "ENERGY":           {"addr":0x09, "size":5, "permission":"RO", "data":0x0000000000},
        "CHARGE":           {"addr":0x0A, "size":5, "permission":"RO", "data":0x0000000000},
        "DIAG_ALRT":        {"addr":0x0B, "size":2, "permission":"NA", "data":0x0001}, #This register has different read/write permissions per bit; must be handled individually
        "SOVL":             {"addr":0x0C, "size":2, "permission":"RW", "data":0x7FFF},
        "SUVL":             {"addr":0x0D, "size":2, "permission":"RW", "data":0x8000},
        "BOVL":             {"addr":0x0E, "size":2, "permission":"RW", "data":0x7FFF},
        "BUVL":             {"addr":0x0F, "size":2, "permission":"RW", "data":0x0000},
        "TEMP_LIMIT":       {"addr":0x10, "size":2, "permission":"RW", "data":0x7FFF},
        "PWR_LIMIT":        {"addr":0x11, "size":2, "permission":"RW", "data":0xFFFF},
        "MANUFACTURER_ID":  {"addr":0x3E, "size":2, "permission":"RO", "data":0x5449},
        "DEVICE_ID":        {"addr":0x3F, "size":2, "permission":"RO", "data":0x2291},
    }
    _conversion_time_us_to_bin = bidict({50:0, 84:1, 150:2, 280:3, 540:4, 1052:5, 2074:6, 4120:7})
    _mode_str_to_bin = bidict({
        "SHUTDOWN": 0x0,
        "TRG_VOLT_ONLY": 0x1, #Triggered bus voltage, single shot
        "TRG_CURR_ONLY": 0x2, #Triggered shunt voltage, single shot
        "TRG_VOLT_CURR": 0x3, #Triggered shunt voltage and bus voltage, single shot
        "TRG_TEMP_ONLY": 0x4, #Triggered temperature, single shot
        "TRG_VOLT_TEMP": 0x5, #Triggered temperature and bus voltage, single shot
        "TRG_CURR_TEMP": 0x6, #Triggered temperature and shunt voltage, single shot
        "TRG_VOLT_CURR_TEMP": 0x7, #Triggered bus voltage, shunt voltage and temperature, single shot
        "SHUTDOWN": 0x8, #Shutdown
        "CONT_VOLT_ONLY": 0x9, #Continuous bus voltage only
        "CONT_CURR_ONLY": 0xA, #Continuous shunt voltage only
        "CONT_VOLT_CURR": 0xB, #Continuous shunt and bus voltage
        "CONT_TEMP_ONLY": 0xC, #Continuous temperature only
        "CONT_VOLT_TEMP": 0xD, #Continuous bus voltage and temperature
        "CONT_CURR_TEMP": 0xE, #Continuous temperature and shunt voltage
        "CONT_VOLT_CURR_TEMP": 0xF, #Continuous bus voltage, shunt voltage and temperature
    })
    _adc_config_to_bin_mask = {"averaging_count": 0, "temperature":3, "current":6, "voltage":9, "mode": 13}

    spi_mode: ClassVar[int] = 1
    min_spi_max_speed: ClassVar[float] = 1e7
    max_spi_max_speed: ClassVar[float] = 0e1
    spi_bit_order: ClassVar[str] = 'msb'
    spi_word_bit_count: ClassVar[int] = 8
    reference_voltage: ClassVar[float] = 3.3
    divisor: ClassVar[float] = 1048576 #20-bit
    spi: SPI

    # CONSTANTS
    _max_queue_size = 1000

    def __post_init__(self, nbr_avg_voltage:int=10, nbr_avg_current:int=10, nbr_avg_temperature:int=20) -> None:
        self._voltage_queue = collections.deque(maxlen=nbr_avg_voltage)
        self._current_queue = collections.deque(maxlen=nbr_avg_current)
        self._temperature_queue = collections.deque(maxlen=nbr_avg_temperature)
        pass

    def run10ms(self):
        pass

# # # # # # # # # # # # # # # # # # # # # # # #
#             P R O P E R T I E S             #
# # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def voltage_filtered(self) -> float:
        if len(self._voltage_queue) == 0: return 0
        else: return sum(self._voltage_queue)/len(self._voltage_queue)

    @property
    def voltage_raw(self) -> float:
        if len(self._voltage_queue) == 0: return 0
        else: return self._voltage_queue[-1]

    @property
    def current_filtered(self) -> float:
        if len(self._current_queue) == 0: return 0
        else: return sum(self._current_queue)/len(self._current_queue)

    @property
    def current_raw(self) -> float:
        if len(self._current_queue) == 0: return 0
        else: return self._current_queue[-1]

    @property
    def temperature_filtered(self) -> float:
        if len(self._temperature_queue) == 0: return 0
        else: return sum(self._temperature_queue)/len(self._temperature_queue)

    @property
    def temperature_raw(self) -> float:
        if len(self._temperature_queue) == 0: return 0
        else: return self._temperature_queue[-1]

    @property
    def mode(self) -> str:
        masked_data = self._register_map["ADC_CONFIG"][3] & (0b111 << self._adc_config_to_bin_mask["mode"])
        return self._mode_str_to_bin.inverse[masked_data >> self._adc_config_to_bin_mask["mode"]]

    @mode.setter
    def mode(self, desired_mode:str) -> None:
        if desired_mode not in self._mode_str_to_bin.keys(): raise Exception(f"Mode {desired_mode} unavailable on INA229.")

        mode_bin = self._mode_str_to_bin[desired_mode]
        mask = 0b111 << self._adc_config_to_bin_mask["mode"]
        data:int = (self._register_map["ADC_CONFIG"][3] & ~mask) | (mode_bin << self._adc_config_to_bin_mask["mode"])
        length = self._register_map["ADC_CONFIG"][1]
        self._write_to_SPI("ADC_CONFIG", data=data.to_bytes(length, "big"))
        self._register_map["ADC_CONFIG"]["data"] = data

    @property
    def voltage_conversion_time(self) -> int:
        mask = self._adc_config_to_bin_mask["voltage"]
        masked_data = self._register_map["ADC_CONFIG"]["data"] & (0b111 << mask)
        return self._conversion_time_us_to_bin.inverse[masked_data >> mask]

    @voltage_conversion_time.setter
    def voltage_conversion_time(self, conversion_time: int) -> None:        
        self._write_conversion_time(measurement="voltage", conversion_time=conversion_time)

    @property
    def current_conversion_time(self) -> int:
        mask = self._adc_config_to_bin_mask["current"]
        masked_data = self._register_map["ADC_CONFIG"]["data"] & (0b111 << mask)
        return self._conversion_time_us_to_bin.inverse[masked_data >> mask]

    @current_conversion_time.setter
    def current_conversion_time(self, conversion_time: int) -> None:        
        self._write_conversion_time(measurement="current", conversion_time=conversion_time)

    @property
    def temperature_conversion_time(self) -> int:
        mask = self._adc_config_to_bin_mask["temperature"]
        masked_data = self._register_map["ADC_CONFIG"]["data"] & (0b111 << mask)
        return self._conversion_time_us_to_bin.inverse[masked_data >> mask]

    @temperature_conversion_time.setter
    def temperature_conversion_time(self, conversion_time: int) -> None:        
        self._write_conversion_time(measurement="temperature", conversion_time=conversion_time)

    #Not implemented
    @property
    def diagnostics_alert(self) -> float:
        raise NotImplementedError("Access to 'DIAG_ALRT' register not yet implemented.")
    @property
    def overcurrent_threshold(self) -> float:
        raise NotImplementedError("Access to 'SOVL' register not yet implemented.")
    @property
    def undercurrent_threshold(self) -> float:
        raise NotImplementedError("Access to 'SUVL' register not yet implemented.")
    @property
    def overvoltage_threshold(self) -> float:
        raise NotImplementedError("Access to 'BOVL' register not yet implemented.")
    @property
    def undervoltage_threshold(self) -> float:
        raise NotImplementedError("Access to 'BUVL' register not yet implemented.")
    @property
    def temperature_limit(self) -> float:
        raise NotImplementedError("Access to 'TEMP_LIMIT' register not yet implemented.")
    @property
    def power_limit(self) -> float:
        raise NotImplementedError("Access to 'PWR_LIMIT' register not yet implemented.")
    @property
    def manufacturer_id(self) -> float:
        raise NotImplementedError("Access to 'MANUFACTURER_ID' register not yet implemented.")
    @property
    def device_id(self) -> float:
        raise NotImplementedError("Access to 'DEVICE_ID' register not yet implemented.")

# # # # # # # # # # # # # # # # # # # # # # # #
#               H E L P E R S                 #
# # # # # # # # # # # # # # # # # # # # # # # #

    def _write_to_SPI(self, register: str, data: (bytes | bytearray | list[int])) -> None:
        if register not in self._register_map.keys(): raise Exception(f"Register '{register}' not supported on the INA229.")
        if self._register_map[register]["permission"] != "RW": raise PermissionError(f"Write to register '{register}' is not permitted.")
        addr = self._register_map[register]["addr"]
        self.spi.transfer(addr << 2 + data) #TODO: Check byte order
    
    def _read_from_SPI(self, register: str) -> (bytes | bytearray | list[int]):
        if register not in self._register_map.keys(): raise Exception(f"Register '{register}' not supported on the INA229.")
        addr = self._register_map[register]["addr"]
        data_received = self.spi.transfer(addr << 2 | 0x1) #TODO: Check byte order
        self._register_map[register]["data"] = data_received
        return data_received

    def _write_conversion_time(self, measurement: str, conversion_time: int) -> None:
        if measurement not in self._adc_config_to_bin_mask.keys(): raise Exception(f"Measurement {measurement} is invalid. Must be one of 'temperature', 'voltage' or 'current'.")
        if conversion_time not in self._conversion_time_us_to_bin.keys(): raise Exception(f"Conversion time {conversion_time}us is invalid; must be one of 50us, 84us, 150us, 280us, 540us, 1052us, 2074us or 4120us.")

        mask = self._adc_config_to_bin_mask[measurement]
        conversion_time_bin = self._conversion_time_us_to_bin[conversion_time]

        existing_data = int.from_bytes(self._read_from_SPI("ADC_CONFIG"), "big")

        data_to_send = (existing_data & ~(0b111 << mask)) | (conversion_time_bin << mask)

        self.spi._write_to_SPI("ADC_CONFIG", data_to_send)
        self._register_map["ADC_CONFIG"]["data"] = data_to_send
