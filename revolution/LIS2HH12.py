from dataclasses import dataclass
from enum import IntEnum

from periphery import I2C

from iclib.utilities import twos_complement

class Register(IntEnum):
    WHO_AM_I_REG = 0x0F
    CTRL1_REG = 0x20
    CTRL4_REG = 0x23
    OUT_X_L = 0x28

@dataclass
class LIS2HH12:
    i2c: I2C
    address: int

    @dataclass
    class Vector:
        x: float
        y: float
        z: float

    def write(self, register: Register, data: int) -> None:
        message = I2C.Message([register, data])

        self.i2c.transfer(self.address, [message])

    def read(self, register: Register, length: int) -> list[int]:
        write_message = I2C.Message([register])
        read_message = I2C.Message([0] * length, read=True)
        self.i2c.transfer(self.address, [write_message, read_message])

        return list(read_message.data)

    def close(self) -> None:
        self.i2c.close()

    def config(self) -> None:
        self.write(Register.CTRL1_REG, 0x37) 
        # Configure CTRL1: ODR=100 Hz (0b0111 << 4) + enable XYZ (0b111)
        self.write(Register.CTRL4_REG, 0x34) 
        # Configure CTRL4: enable auto increment (IF_ADD_INC = 1)
        # change scale to 8g

    def read_accel(self) -> 'LIS2HH12.Vector':
        write_message = I2C.Message([Register.OUT_X_L | 0x80])
        read_message = I2C.Message([0] * 6, read=True)
        self.i2c.transfer(self.address, [write_message, read_message])
        raw = read_message.data
        xg = twos_complement((raw[1] << 8 | raw[0]), 16) * 0.244 / 1000.0
        yg = twos_complement((raw[3] << 8 | raw[2]), 16) * 0.244 / 1000.0
        zg = twos_complement((raw[5] << 8 | raw[4]), 16) * 0.244 / 1000.0
        return self.Vector(xg, yg, zg)
