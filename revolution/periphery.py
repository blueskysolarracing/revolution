__all__ = (
    'GPIO',
    'MockGPIO',
    'MockSPI',
    'SPI',
    'gpio_patcher',
    'spi_patcher',
)

from itertools import repeat, starmap
from os import environ
from unittest.mock import MagicMock, patch

if environ.get('TORADEX', '0') != '1':
    gpio_patcher = patch('periphery.GPIO')
    spi_patcher = patch('periphery.SPI')
    MockGPIO = gpio_patcher.start()
    MockSPI = spi_patcher.start()
    MockGPIO.side_effect = starmap(MagicMock, repeat(()))
    MockSPI.side_effect = starmap(MagicMock, repeat(()))

from periphery import GPIO, SPI
