from time import sleep
from unittest.mock import MagicMock

from iclib.bno055 import BNO055
from periphery import GPIO, I2C

ORIENTATION_IMU_BNO055_I2C: I2C = I2C('/dev/apalis-i2c3')
ORIENTATION_IMU_BNO055_IMU_RESET_GPIO: GPIO = MagicMock(
    direction='out',
    inverted=True,
)
ORIENTATION_IMU_BNO055: BNO055 = BNO055(
    ORIENTATION_IMU_BNO055_I2C,
    ORIENTATION_IMU_BNO055_IMU_RESET_GPIO,
)

raw = ORIENTATION_IMU_BNO055.read(0x00, 1)
print(f'raw: {raw}')

while True:
    with environment.contexts() as ctx:
        print(
            f"L:{ctx.miscellaneous_left_wheel_accelerations} | "
            f"R:{ctx.miscellaneous_right_wheel_accelerations}"
        )
    sleep(0.5)