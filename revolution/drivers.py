from dataclasses import dataclass
from enum import IntEnum
from periphery import SPI
from typing import ClassVar
from warnings import warn


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
