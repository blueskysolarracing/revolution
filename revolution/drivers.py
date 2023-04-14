import math
from dataclasses import dataclass
from enum import IntEnum
from logging import getLogger
from math import inf
from time import sleep, time
from typing import ClassVar, Optional
from warnings import warn

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
class LTC6810:
    spi_mode: ClassVar[int] = 3  # TODO: read document
    """The supported spi mode."""
    max_spi_max_speed: ClassVar[float] = 1e6  # TODO: read document
    """The supported maximum spi maximum speed."""
    spi_bit_order: ClassVar[str] = 'msb'
    """The supported spi bit order."""
    spi_word_bit_count: ClassVar[int] = 8
    """The supported spi number of bits per word."""
    reference_voltage: ClassVar[float] = 3.3
    """The reference voltage value (in volts)."""
    spi: SPI
    """The SPI for the device."""
    gpio_b: GPIO
    """The GPIO for the device."""
    NUM_TEMP_SENSORS: ClassVar[int] = 3
    NUM_VOLTAGES: ClassVar[int] = 5
    address_mode_id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.spi.mode != self.spi_mode:
            raise ValueError('unsupported spi mode')
        elif not self.spi.max_speed <= self.max_spi_max_speed:
            raise ValueError('unsupported spi maximum speed')
        elif self.spi.bit_order != self.spi_bit_order:
            raise ValueError('unsupported spi bit order')
        elif self.spi.bits_per_word != self.spi_word_bit_count:
            raise ValueError('unsupported spi number of bits per word')

        if self.spi.extra_flags:
            warn('unknown spi extra flags')

    def initialize_board(self, gpio_4: int, gpio_3: int, gpio_2: int, dcc_5: int, dcc_4: int, dcc_3: int, dcc_2: int, dcc_1: int) -> None:
        """
        Initialize the LTC6810 ADC chip
        To modify the initialization setting, please refer to the Datasheet and the chart below
         +-------+---------+---------+---------+---------+---------+---------+---------+--------+
         | reg   | Bit7    | Bit6    | Bit5    | Bit4    | Bit3    | Bit2    | Bit1    | Bit0   |
         +-------+---------+---------+---------+---------+---------+---------+---------+--------+
         | CFGR0 | RSVD    | GPIO4   | GPIO3   | GPIO2   | GPIO1   | REFON   | DTEN    | ADCOPT |
         +-------+---------+---------+---------+---------+---------+---------+---------+--------+
         | CFGR1 | VUV[7]  | VUV[6]  | VUV[5]  | VUV[4]  | VUV[3]  | VUV[2]  | VUV[1]  | VUV[0] |
         +-------+---------+---------+---------+---------+---------+---------+---------+--------+
         | CFGR2 | VOV[3]  | VOV[2]  | VOV[1]  | VOV[0]  | VUV[11] | VUV[10] | VUV[9]  | VUV[8] |
         +-------+---------+---------+---------+---------+---------+---------+---------+--------+
         | CFGR3 | VOV[11] | VOV[10] | VOV[9]  | VOV[8]  | VOV[7]  | VOV[6]  | VOV[5]  | VOV[4] |
         +-------+---------+---------+---------+---------+---------+---------+---------+--------+
         | CFGR4 | DCC0    | MCAL    | DCC6    | DCC5    | DCC4    | DCC3    | DCC2    | DCC1   |
         +-------+---------+---------+---------+---------+---------+---------+---------+--------+
         | CFGR5 | DCTO[3] | DCTO[2] | DCTO[1] | DCTO[0] | SCONV   | FDRF    | DIS_RED | DTMEN  |
         +-------+---------+---------+---------+---------+---------+---------+---------+--------+
         Connection to MUX for thermal measurements:
         GPIO1 -> A0
         GPIO3 -> A1
         GPIO4 -> A2
         GPIO1 shall always be set to 1 to avoid internal pull-down, as its the voltage reading pin.
         A2 is MSB and A0 is MSB, if want channel 2 -> do A2=0, A1=1, A0=0
        """
        data_to_send = self.generate_data_to_send(gpio_4, gpio_3, gpio_2, dcc_5, dcc_4, dcc_3, dcc_2, dcc_1)
        self.spi.transfer(data_to_send)

    def generate_data_to_send(self, gpio_4: int, gpio_3: int, gpio_2: int, dcc_5: int, dcc_4: int, dcc_3: int, dcc_2: int, dcc_1: int) -> list[int]:
        """
        Generate the data to send to the LTC6810 chip based on pin configuration
        :return: array of data to send to the chip
        """
        data_6_byte = [0] * 48  # [47] is MSB, CFGR0 Bit7
        # stores command and PEC bit of WRCFG [2 byte command, 2 byte PEC, 6 byte data, 2 byte PEC]
        data_to_send = [0] * 12

        # write configure command
        message_in_binary = 0b1
        self.generate_command_address_mode(message_in_binary, data_to_send)

        '''
        Set GPIO bits to 1 so they aren`t being pulled down internally by the chip
        Set REFON to enable the 3V that goes to the chip
        DTEN to 0 to disable discharge timer
        ADCOPT bit to 0, use 422Hz as its stable
        Above are byte0, byte 1 full of 0s as VUV currently not used
        '''
        message_in_binary = 0b0000110000000000  # CFGR0&1
        message_in_binary += 4096 * gpio_2 + 8192 * gpio_3 + 16384 * gpio_4

        msg_0, msg_1 = self.command_to_array(message_in_binary)
        for i in range(8):
            data_6_byte[40 + i] = msg_0[i]
            data_6_byte[32 + i] = msg_1[i]

        # Set the VOV and VUV as 0
        message_in_binary = 0b0000000000000000  # CFGR2&3
        msg_2, msg_3 = self.command_to_array(message_in_binary)
        for i in range(8):
            data_6_byte[24 + i] = msg_2[i]
            data_6_byte[16 + i] = msg_3[i]

        '''
        DCC = 0: discharge off, 1: discharge = on
        MCAL = 1: enable multi-calibration. for this don`t use, turn to 0
        DCTO: discharge timer. for now 0
        SCONV: redundant measurement using S pin, disable for now (0)
        FDRF: not using it anyway, to 0
        DIS_RED: redundancy disable: set to 1 to disable
        DTMEN: Discharge timer monitor, 0 to disable
        '''
        message_in_binary = 0b0000000000000010
        message_in_binary += 256 * dcc_1 + 512 * dcc_2 + 1024 * dcc_3 + 2048 * dcc_4 + 4096 * dcc_5
        msg_4, msg_5 = self.command_to_array(message_in_binary)
        for i in range(8):
            data_6_byte[8 + i] = msg_4[i]
            data_6_byte[0 + i] = msg_5[i]

        # generate PEC bits based on above data
        pec0_6bytes, pec1_6bytes = self.generate_pec_bits(True, data_6_byte)

        # change array back to bytes
        data_to_send[4] = self.array_to_byte(msg_0)
        data_to_send[5] = self.array_to_byte(msg_1)
        data_to_send[6] = self.array_to_byte(msg_2)
        data_to_send[7] = self.array_to_byte(msg_3)
        data_to_send[8] = self.array_to_byte(msg_4)
        data_to_send[9] = self.array_to_byte(msg_5)
        data_to_send[10] = self.array_to_byte(pec0_6bytes)
        data_to_send[11] = self.array_to_byte(pec1_6bytes)

        return data_to_send

    @staticmethod
    # combined LTC6810GeneratePECbits and LTC6810GeneratePECbits6Byte from GEN11
    def generate_pec_bits(is_6_bytes: bool, data: list[int], cmd1: Optional[list[int]] = None) -> tuple[list[int], list[int]]:
        """
        Generate PEC bits based on 6-byte data or commands
        :param is_6_bytes: whether to generate PEC bits based on 6-byte data
        :param data: 6-byte data or command array
        :param cmd1: additional command array for non-6-byte data PEC generation
        :return: None
        """
        pec_0 = [0] * 8
        pec_1 = [0] * 8
        # initialize the 15 bit pec. in last cycle shift up add 0 at LSB
        pec = [0] * 15
        pec[4] = 1

        # note for 6 bytes data, data[47] is 1st bit
        iterations = 47 if is_6_bytes else 15
        for i in range(iterations, -1, -1):
            # step 1: assign DIN value
            if is_6_bytes:
                din = data[i]
            elif cmd1 is not None:
                din = data[i - 8] if i >= 8 else cmd1[i]

            # step 2: shifting
            in0 = din ^ pec[14]
            in3 = in0 ^ pec[2]
            in4 = in0 ^ pec[3]
            in7 = in0 ^ pec[6]
            in8 = in0 ^ pec[7]
            in10 = in0 ^ pec[9]
            in14 = in0 ^ pec[13]

            # step 3: shifting
            pec[14] = in14
            pec[13] = pec[12]
            pec[12] = pec[11]
            pec[11] = pec[10]
            pec[10] = in10
            pec[9] = pec[8]
            pec[8] = in8
            pec[7] = in7
            pec[6] = pec[5]
            pec[5] = pec[4]
            pec[4] = in4
            pec[3] = in3
            pec[2] = pec[1]
            pec[1] = pec[0]
            pec[0] = in0

        # adjusting pec_0 and pec_1
        for j in range(14, -1, -1):
            if j >= 7:
                pec_0[j - 7] = pec[j]
            else:
                pec_1[j + 1] = pec[j]

        # add 0 at the end to make it 2 bytes
        pec_1[0] = 0
        return pec_0, pec_1

    @staticmethod
    def array_to_byte(in_array: list[int]) -> int:
        """
        Converting array containing 8 bits to byte
        :return: 8-bit unsigned integer
        """
        # note: [7] is MSB, [0] is LSB
        bit_str = "".join(str(bit) for bit in in_array[::-1])
        return int(bit_str, 2)

    @staticmethod
    def command_to_array(command: int) -> tuple[list[int], list[int]]:
        """
        Given command, convert into two binary arrays
        :param command: message in binary
        :return: two binary arrays
        """
        cmd0_ref = [0] * 8
        cmd1_ref = [0] * 8
        for i in range(16):  # from LSB to MSB, fill cmd1 first
            temp_bit = command % 2
            if i <= 7:
                cmd1_ref[i] = temp_bit
            else:
                cmd0_ref[i - 8] = temp_bit

            command = command >> 1  # right shift to remove LSB

        return cmd0_ref, cmd1_ref

    def generate_command_address_mode(self, command: int, data_to_send: list[int]) -> None:
        """
        Generate command for address mode. If address mode is not enabled, broadcast mode is used
        :param command: command to convert
        :param data_to_send: array of integer containing message and error check
        :return: None
        """
        if self.address_mode_id:
            address_command = (0b10000 | (self.address_mode_id & 0b1111)) << 12
            command |= address_command
        self.generate_command(command, data_to_send)

    def generate_command(self, command: int, data_to_send: list[int]) -> None:
        """
        Fill in data_to_send with command and error checking bits
        :param command: command to convert
        :param data_to_send: array of integer containing message and error check
        :return: None
        """
        # convert command into two separate array
        cmd0_list, cmd1_list = self.command_to_array(command)

        # generate error checking bits
        pec_bits_0, pec_bits_1 = self.generate_pec_bits(False, cmd0_list, cmd1_list)

        # put data back into data_to_send list, with size of 4
        data_to_send[0] = self.array_to_byte(cmd0_list)  # 1st byte message
        data_to_send[1] = self.array_to_byte(cmd1_list)  # 2nd byte message
        data_to_send[2] = self.array_to_byte(pec_bits_0)  # 1st byte error check
        data_to_send[3] = self.array_to_byte(pec_bits_1)  # 2nd byte error check

    def isospi_wakeup(self) -> None:
        """
        Wake up the LTC6810 from sleep mode.
        :return: None
        """
        # No delay more than 3ms allowed (between this function call and the actual SPI comm)! else isoSPI might go back to sleep
        # Need to transmit dummy byte
        dummy_byte = [0]
        self.spi.transfer(dummy_byte)

    @staticmethod
    def data_to_voltage(low_byte: int, high_byte: int) -> int:
        """
        Calculate final voltage based on (total - 8192) * 100uV
        Based on LTC6810 datasheet, every bit is 100uV
        Full range of 16 bytes: -0.8192 to + 5.7344
        :param low_byte: low byte of data (uint8_t)
        :param high_byte: high byte of data (uint8_t)
        :return: converted voltage
        """
        return low_byte + high_byte * 256

    def voltage_to_temp(self, input_voltage: list[float]) -> list[float]:
        """
        Convert raw ADC code to temperature
        :param input_voltage: list of voltage values
        :return: list of temperature values
        """
        output_temperature = [0.0] * 3
        temp_correction_multiplier = 1.0
        temp_correction_offset = 0.0
        for i in range(self.NUM_TEMP_SENSORS):
            corrected_voltage = temp_correction_multiplier * (input_voltage[i] / 10000.0 - temp_correction_offset)
            thermistor_resistance = 10.0 / ((2.8 / corrected_voltage) - 1.0)
            output_temperature[i] = 1.0 / (0.003356 + 0.0002532 * math.log(thermistor_resistance / 10.0))
            output_temperature[i] = output_temperature[i] - 273.15

            # Preventing NaN (treated as 0xFFFFFFFF) from tripping the battery safety but lower-bounding them to -100C
            # This occurs when the measurement is closes to 3V, suggesting that the thermistor isn't connected
            if thermistor_resistance < 0:
                output_temperature[i] = -100.0

        return output_temperature

    def read_temp(self, dcc_5: int, dcc_4: int, dcc_3: int, dcc_2: int, dcc_1: int) -> list[float]:
        """
        Read temperature from LTC6810
        :param dcc_5: DCC5 pin
        :param dcc_4: DCC4 pin
        :param dcc_3: DCC3 pin
        :param dcc_2: DCC2 pin
        :param dcc_1: DCC1 pin
        :return: list of temperature values
        """
        temp_array = [0.0] * self.NUM_TEMP_SENSORS
        data_to_send = [0] * 16
        for cycle in range(3):
            if cycle == 0:
                self.initialize_board(0, 0, 0, dcc_5, dcc_4, dcc_3, dcc_2, dcc_1)  # channel 1
            elif cycle == 1:
                self.initialize_board(0, 0, 1, dcc_5, dcc_4, dcc_3, dcc_2, dcc_1)  # channel 2
            elif cycle == 2:
                self.initialize_board(0, 1, 0, dcc_5, dcc_4, dcc_3, dcc_2, dcc_1)  # channel 3

            message_in_binary = 0b10100010010  # conversion GPIO1, command AXOW
            self.generate_command_address_mode(message_in_binary, data_to_send)
            self.spi.transfer(data_to_send[:4])  # send 4 bytes of data

            # receive data
            message_in_binary = 0b1100  # read auxiliary group 1, command RDAUXA
            self.generate_command_address_mode(message_in_binary, data_to_send)
            data_to_receive = self.spi.transfer(data_to_send)  # receive temp data from LTC6810 via SPI

            # write value into array
            temp_array[cycle] = 256 * data_to_receive[3] + data_to_receive[2]

        return temp_array

    def read_voltage(self) -> list[float]:
        """
        Read voltage from LTC6810
        :return: array of voltage readings
        """
        volt_array = [0.0] * self.NUM_VOLTAGES
        data_to_send = [0] * 4  # data organized by LTC6810.generate_command()
        # data_to_receive = [0] * 8  # voltage data from LTC6810 via SPI

        # read first half of data
        vmessage_in_binary = 0b01101110000  # adcv discharge enable,7Hz
        self.generate_command_address_mode(vmessage_in_binary, data_to_send)  # generate the "check voltage command"
        data_to_receive = self.spi.transfer(data_to_send)

        vmessage_in_binary = 0b100  # read cell voltage reg group 1
        self.generate_command_address_mode(vmessage_in_binary, data_to_send)
        data_to_receive = self.spi.transfer(data_to_send)

        volt_array[0] = self.data_to_voltage(data_to_receive[0], data_to_receive[1]) / 10000.0
        volt_array[1] = self.data_to_voltage(data_to_receive[2], data_to_receive[3]) / 10000.0
        volt_array[2] = self.data_to_voltage(data_to_receive[4], data_to_receive[5]) / 10000.0

        vmessage_in_binary = 0b110  # read cell voltage reg group 2
        self.generate_command_address_mode(vmessage_in_binary, data_to_send)
        data_to_receive = self.spi.transfer(data_to_send)
        self.gpio_b.write(True)  # TODO: check if this is still needed

        volt_array[3] = self.data_to_voltage(data_to_receive[0], data_to_receive[1]) / 10000.0
        volt_array[4] = self.data_to_voltage(data_to_receive[2], data_to_receive[3]) / 10000.0

        return volt_array
