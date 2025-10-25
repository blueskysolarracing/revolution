from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import ClassVar
from warnings import warn

from periphery import GPIO, SPI


class DisplayItem(IntEnum):
    BAT_HEADER      = 0
    VEL_HEADER      = 1
    VELOCITY        = 2
    VELOCITY_UNIT   = 3
    CRUISE_CTRL     = 4
    CRUISE_CTRL_VEL = 5
    REGEN           = 6
    VFM             = 7
    VFM_GEAR        = 8

    BAT_SOC         = 9
    BAT_SOC_UNIT    = 10
    SAFE_STATE      = 11
    BMS_VOLT        = 12
    BMS_TEMP        = 13
    BMS_CURRENT     = 14


class InputByte(IntEnum):
    BYTE_0 = 0x00
    BYTE_1 = 0x01


class InputBit(IntEnum):
    BIT_0 = 0x00
    BIT_1 = 0x01
    BIT_2 = 0x02
    BIT_3 = 0x03
    BIT_4 = 0x04
    BIT_5 = 0x05
    BIT_6 = 0x06
    BIT_7 = 0x07


class InputByteBit(tuple[InputByte, InputBit], Enum):
    BB_00 = InputByte.BYTE_0, InputBit.BIT_0
    BB_01 = InputByte.BYTE_0, InputBit.BIT_1
    BB_02 = InputByte.BYTE_0, InputBit.BIT_2
    BB_03 = InputByte.BYTE_0, InputBit.BIT_3
    BB_04 = InputByte.BYTE_0, InputBit.BIT_4
    BB_05 = InputByte.BYTE_0, InputBit.BIT_5
    BB_06 = InputByte.BYTE_0, InputBit.BIT_6
    BB_07 = InputByte.BYTE_0, InputBit.BIT_7
    BB_10 = InputByte.BYTE_1, InputBit.BIT_0
    BB_11 = InputByte.BYTE_1, InputBit.BIT_1
    BB_12 = InputByte.BYTE_1, InputBit.BIT_2
    BB_13 = InputByte.BYTE_1, InputBit.BIT_3
    BB_14 = InputByte.BYTE_1, InputBit.BIT_4
    BB_15 = InputByte.BYTE_1, InputBit.BIT_5
    BB_16 = InputByte.BYTE_1, InputBit.BIT_6
    BB_17 = InputByte.BYTE_1, InputBit.BIT_7


@dataclass
class SteeringWheel:
    SPI_MODE: ClassVar[int] = 0b00
    """The supported spi mode."""
    MIN_SPI_MAX_SPEED: ClassVar[float] = 5e4
    """The supported minimum spi maximum speed."""
    MAX_SPI_MAX_SPEED: ClassVar[float] = 8e6
    """The supported maximum spi maximum speed."""
    SPI_BIT_ORDER: ClassVar[str] = 'msb'
    """The supported spi bit order."""
    SPI_WORD_BIT_COUNT: ClassVar[int] = 8
    """The supported spi number of bits per word."""
    spi: SPI
    """The SPI for the steering wheel."""
    interrupt_gpio: GPIO
    """The interrupt pin for button toggles."""
    fault_light_gpio: GPIO
    """The LED for BPS fault."""

    def __post_init__(self) -> None:
        if self.spi.mode != self.SPI_MODE:
            raise ValueError('unsupported spi mode')
        elif not (
                self.MIN_SPI_MAX_SPEED
                <= self.spi.max_speed
                <= self.MAX_SPI_MAX_SPEED
        ):
            raise ValueError('unsupported spi maximum speed')
        elif self.spi.bit_order != self.SPI_BIT_ORDER:
            raise ValueError('unsupported spi bit order')
        elif self.spi.bits_per_word != self.SPI_WORD_BIT_COUNT:
            raise ValueError('unsupported spi number of bits per word')

        if self.spi.extra_flags:
            warn(f'unknown spi extra flags {self.spi.extra_flags}')

        # add gpio checks

    def clear_screen(self) -> None:
        for i in range(32):
            self.draw_word(i, '')

    def set_text_position(self, slot: DisplayItem, x: int, y: int) -> None:
        if (
            not (0 <= slot <= 31) or not (0 <= x <= 536) or not (0 <= y <= 42)
        ):
            return

        message = [(1 << 7) | ((slot << 2) & 0x1F) | 0b00]
        message += [(x >> 8) & 0xFF, x & 0xFF, (y >> 8) & 0xFF, y & 0xFF]
        self.spi.transfer(message)

    def set_text_size(self, slot: DisplayItem, size: int) -> None:
        if (not (0 <= slot <= 31) or not (1 <= size <= 16)):
            return

        message = [(1 << 7) | ((slot << 2) & 0x0F) | 0b01]
        message.append(size)
        self.spi.transfer(message)

    def set_text_mode(self, slot: DisplayItem, mode: int) -> None:
        if (not (0 <= slot <= 31) or not (0 <= mode <= 7)):
            return                                                
                                                               
        message = [(1 << 7) | ((slot & 0x1F) << 2) | 0b10]             
        message.append(mode)                                      
        self.spi.transfer(message)

    def draw_word(self, slot: DisplayItem, text: str) -> None:
        if (not (0 <= slot <= 31)):
            return

        message = [(1 << 7) | ((slot << 2) & 0x1F) | 0b11]
        message.append(len(text))
        message += list(text.encode('utf-8'))
        self.spi.transfer(message)

    def set_display_brightness(self, brightness: int) -> None:
        if (not (0 <= brightness <= 100)):
            return

        message = [0x03, brightness]
        self.spi.transfer(message)

    def set_indicator_light(self, left: bool, right: bool) -> None:
        status = left << 1 | right
        message = [0x02, status]
        self.spi.transfer(message)

    def set_fault_light(self, status: bool) -> None:
        message = [0x01, int(status)]
        self.spi.transfer(message)

    def get_input(self) -> list[int]:

        def bitwise_majority(values):
            result = 0
            for bit in range(8):
                mask = 1 << bit
                count = sum((v & mask) != 0 for v in values)
                if count > 15:
                    result |= mask
            return result

        replicate = 19
        raw = []
        for i in range(replicate):
            raw += self.spi.transfer([0x00] * replicate)
        
        flipped = [((~x) & 0xFF) for x in raw]
        first_bytes = flipped[0::2]
        second_bytes = flipped[1::2]
        return [bitwise_majority(first_bytes), bitwise_majority(second_bytes)]
