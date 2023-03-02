from os import environ
from periphery import GPIO as GPIO, SPI as SPI
from unittest.mock import MagicMock

if environ.get('TORADEX') != '1':
    GPIO = MagicMock  # type: ignore [misc]  # noqa: F811
    SPI = MagicMock  # type: ignore [misc]  # noqa: F811
