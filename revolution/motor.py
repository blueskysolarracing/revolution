from dataclasses import dataclass
from logging import getLogger
from periphery import GPIO, SPI
from time import sleep
from typing import ClassVar

from revolution.application import Application
from revolution.environment import Direction, Endpoint

_logger = getLogger(__name__)


class MotorController:
    @staticmethod
    def __position_potentiometer(
            spi: SPI,
            position: int,
            eeprom: bool,
    ) -> None:
        if not 0 <= position <= 256:
            raise ValueError('position not between 0 and 256')

        raw_data = position

        if eeprom:
            raw_data |= 1 << 13

        data = [raw_data >> 8, raw_data & ((1 << 8) - 1)]

        spi.transfer(data)

    acceleration_potentiometer_spi: ClassVar[SPI] = SPI('', 0, 1)  # TODO
    regeneration_potentiometer_spi: ClassVar[SPI] = SPI('', 0, 1)  # TODO
    main_switch_gpio: ClassVar[GPIO] = GPIO('', 0, 'out')  # TODO
    forward_or_reverse_switch_gpio: ClassVar[GPIO] = GPIO('', 0, 'out')  # TODO
    power_or_economical_switch_gpio: ClassVar[GPIO] \
        = GPIO('', 0, 'out')  # TODO
    vfm_up_switch_gpio: ClassVar[GPIO] = GPIO('', 0, 'out')  # TODO
    vfm_down_switch_gpio: ClassVar[GPIO] = GPIO('', 0, 'out')  # TODO

    def __post_init__(self) -> None:
        self.accelerate(0, True)
        self.regenerate(0, True)

    def accelerate(self, acceleration: float, eeprom: bool = False) -> None:
        if not 0 <= acceleration <= 1:
            raise ValueError('acceleration not between 0 and 1')

        position = round(256 * acceleration)

        self.__position_potentiometer(
            self.acceleration_potentiometer_spi,
            position,
            eeprom,
        )

    def regenerate(self, regeneration: float, eeprom: bool = False) -> None:
        if not 0 <= regeneration <= 1:
            raise ValueError('regeneration not between 0 and 1')

        position = round(256 * regeneration)

        self.__position_potentiometer(
            self.regeneration_potentiometer_spi,
            position,
            eeprom,
        )

    def state(self, status: bool) -> None:
        wait = status and self.main_switch_gpio.read()

        self.main_switch_gpio.write(not status)

        if wait:
            sleep(5)

    def direct(self, direction: Direction) -> None:
        match direction:
            case Direction.FORWARD:
                raw_direction = False
            case Direction.BACKWARD:
                raw_direction = True
            case _:
                raise ValueError(f'unknown direction {direction}')

        self.forward_or_reverse_switch_gpio.write(raw_direction)

    def economize(self, mode: bool) -> None:
        self.power_or_economical_switch_gpio.write(mode)

    def gear_up(self) -> None:
        self.vfm_up_switch_gpio.write(True)
        sleep(0.2)
        self.vfm_up_switch_gpio.write(False)

    def gear_down(self) -> None:
        self.vfm_down_switch_gpio.write(True)
        sleep(0.2)
        self.vfm_down_switch_gpio.write(False)


@dataclass
class Motor(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.MOTOR
    __controller: ClassVar[MotorController] = MotorController()

    def _setup(self) -> None:
        super()._setup()

    def _teardown(self) -> None:
        super()._teardown()

    def __update_controller(self) -> None:
        with self._environment.read() as data:
            self.__controller.accelerate(data.motor_acceleration_input)
            self.__controller.regenerate(data.motor_regeneration_input)
            self.__controller.state(data.motor_status_input)
            self.__controller.direct(data.motor_directional_input)
            self.__controller.economize(data.motor_economical_mode_input)

    def __update_gears(self) -> None:
        with self._environment.read_and_write() as data:
            if data.motor_gear_input_counter > 0:
                gear_index_input = 1
            elif data.motor_gear_input_counter < 0:
                gear_index_input = -1
            else:
                gear_index_input = 0

            data.motor_gear_input_counter -= gear_index_input

        if gear_index_input > 0:
            self.__controller.gear_up()
        elif gear_index_input < 0:
            self.__controller.gear_down()
