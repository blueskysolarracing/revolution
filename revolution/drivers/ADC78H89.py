"""
    Wrapper for the Texas Instruments ADC78H89 SPI ADC
    Datasheet: https://www.ti.com/lit/ds/symlink/adc78h89.pdf?ts=1677212870525&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252FADC78H89 

    ADC78H89 7-Channel, 500 KSPS, 12-Bit A/D Converter
    -Max. conversion rate: 500KSPS 
    -Data is straight binary, refer to Fig. 23 
    -Each conversion requires 16 CLK cycle, and is triggered when !CS goes low. The conversion is applied to the channel in the Control Register.
     Therefore, there is a one sample delay between writing to the control register and reading the data.
    -Write to the Control Register to select which channel is being sampled: [X X ADD2 ADD1 ADD0 X X X]. Even though this register is 8b, writing to it requires 16 clock cycles since a conversion is taking place in parallel. Only the first 8b are read. 
    -First conversion after power-up is channel #1

    This wrapper also takes in pins that might not to be demuxed to generate the CS signal as a list of "GPIOsConfig". The GPIOs are set to setPolarity before SPI transfer and reset to resetPolarity after.
    CS_GPIOsConfig =   [[GPIO1_devpath, GPIO1_line, GPIO1_setPolarity, GPIO1_resetPolarity], 
                        [GPIO2_devpath, GPIO2_line, GPIO2_setPolarity, GPIO2_resetPolarity], 
                        [GPIO3_devpath, GPIO3_line, GPIO3_setPolarity, GPIO3_resetPolarity], ...]
"""

from enum import Enum
from periphery.spi import SPI
from typing import List, Generator

############# CONSTANTS #############
SPI_MODE = 3
SPI_MAX_SPEED = 1000000 #Supported SPI frequency is 500kHz to 8MHz. Each conversion takes 16/1000000 = 16us.
SPI_BIT_ORDER = 'msb'
SPI_BITS_PER_WORDS = 8
REF_VOLTAGE = 3.3

############## CLASSES ##############
class channel(Enum):
    CHANNEL_1 = 1
    CHANNEL_2 = 2
    CHANNEL_3 = 3
    CHANNEL_4 = 4
    CHANNEL_5 = 5
    CHANNEL_6 = 6
    CHANNEL_7 = 7

class ADC78H89():
    def __init__(self, devpath:str) -> None:
        self.__voltageBuffer = len(channel)*[-1.0]
        self.__spiDev = SPI(devpath, SPI_MODE, SPI_MAX_SPEED, SPI_BIT_ORDER, SPI_BITS_PER_WORDS)

    """
        Returns the last unfiltered voltage
    """
    def getMeasurementRaw(self, ch:Enum) -> float:
        return self.__voltageBuffer[ch.value]

    """
        Handles the SPI calls and updates the voltage buffer. This method is expected to be called every 10ms
    """
    def run10ms(self) -> None:
        for ch in channel:
            nextChannel = ch.value % 7 #Rollover to 0 at last channel
            controlRegister = [(nextChannel << 5), 0x00] #TODO: Need to double-check order that this is sent

            rawData = self.__spiDev.transfer(controlRegister)

            ADCCode = (rawData[0] << 8) + rawData[1] #TODO: Need to double-check order that this is sent
            self.__voltageBuffer[ch.value] = REF_VOLTAGE * (ADCCode / 4096.0)