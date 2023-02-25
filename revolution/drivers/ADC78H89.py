"""
    Wrapper for the Texas Instruments ADC78H89 SPI ADC
    Datasheet: https://www.ti.com/lit/ds/symlink/adc78h89.pdf?ts=1677212870525&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252FADC78H89 

    ADC78H89 7-Channel, 500 KSPS, 12-Bit A/D Converter
    -Max. conversion rate: 500KSPS 
    -Data is straight binary, refer to Fig. 23 
    -Each conversion requires 16 CLK cycle, and is triggered when !CS goes low. The conversion is applied to the channel in the Control Register. Therefore, there is a one sample delay between writing to the control register and reading the data.
    -Write to the Control Register to select which channel is being sampled: [X X ADD2 ADD1 ADD0 X X X]. Even though this register is 8b, writing to it requires 16 clock cycles since a conversion is taking place in parallel. Only the first 8b are read. 
    -First conversion after power-up is channel #1

    This wrapper also takes in pins that might not to be demuxed to generate the CS signal as a list of "GPIOsConfig". The GPIOs are set to setPolarity before SPI transfer and reset to resetPolarity after.
    CS_GPIOsConfig =   [[GPIO1_devpath, GPIO1_line, GPIO1_setPolarity, GPIO1_resetPolarity], 
                        [GPIO2_devpath, GPIO2_line, GPIO2_setPolarity, GPIO2_resetPolarity], 
                        [GPIO3_devpath, GPIO3_line, GPIO3_setPolarity, GPIO3_resetPolarity], ...]
"""

from enum import Enum
from dataclasses import dataclass
from periphery.spi import SPI
from periphery.gpio import GPIO
from typing import List, Generator

############# CONSTANTS #############
SPI_MODE = 3
SPI_MAX_SPEED = 1000000 #Supported SPI frequency is 500kHz to 8MHz. Each conversion takes 16/1000000 = 16us.
SPI_BIT_ORDER = 'msb'
SPI_BITS_PER_WORDS = 8
REF_VOLTAGE = 3.3

############## CLASSES ##############
class channel(Enum):
    CHANNEL_1 = 0
    CHANNEL_2 = 1
    CHANNEL_3 = 2
    CHANNEL_4 = 3
    CHANNEL_5 = 4
    CHANNEL_6 = 5
    CHANNEL_7 = 6

@dataclass
class ADC78H89():
    def __init__(self, devpath:str, CS_GPIOsConfig:list([str, int, bool, bool])) -> None: #TODO: Might want to change this CS_GPIOsConfig structure
        self.__voltageBuffer = len(channel)*[-1.0]
        self.__spiDev = SPI(devpath, SPI_MODE, SPI_MAX_SPEED, SPI_BIT_ORDER, SPI_BITS_PER_WORDS)
        self.__CS_GPIOsConfig = CS_GPIOsConfig

        self.__CS_GPIO: list([Generator, str, int, bool, bool]) = list()
        for GPIOConfig in self.__CS_GPIOsConfig:
            newGPIO = GPIO(devpath=GPIOConfig[0],
                        line=GPIOConfig[1],
                        direction='out')
            self.__CS_GPIO.append([newGPIO] + GPIOConfig)

    """
        Returns the last unfiltered voltage
    """
    def getMeasurementRaw(self, ch:Enum) -> float:
        return self.__voltageBuffer[ch.value]

    def setCS(self) -> None:
        for GPIOConfig in self.__CS_GPIO:
            GPIOConfig[0].write(GPIOConfig[3])

    def resetCS(self) -> None:
        for GPIOConfig in self.__CS_GPIO:
            GPIOConfig[0].write(GPIOConfig[4])

    """
        Handles the SPI calls and updates the voltage buffer. This method is expected to be called every 10ms
    """
    def run10ms(self) -> None:
        for ch in channel:
            nextChannel = (ch.value + 1) % 7 #Rollover to 0 at last channel
            controlRegister = [(nextChannel << 5), 0x00] #TODO: Need to double-check order that this is sent

            self.setCS()
            rawData = self.__spiDev.transfer(controlRegister) #TODO: Understand how this is handled internally to 1) know if to give it a dummy CS GPIO and 2) know how timing will work for CS
            self.resetCS()

            ADCCode = (rawData[0] << 8) + rawData[1] #TODO: Need to double-check order that this is sent
            self.__voltageBuffer[ch.value] = REF_VOLTAGE * (ADCCode / 4096.0)