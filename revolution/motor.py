from dataclasses import dataclass
from multiprocessing import get_logger
from typing import ClassVar

from revolution.application import Application
from revolution.environment import Direction, Endpoint

_logger = get_logger()


class MCP4161:
    def state(self, status: bool) -> None:
        pass  # TODO

    def direct(self, direction: Direction) -> None:
        pass  # TODO

    def accelerate(self, acceleration: float) -> None:
        pass  # TODO

    def regenerate(self, regeneration: float) -> None:
        pass  # TODO

    def economize(self, status: bool) -> None:
        pass  # TODO

    def gear_up(self) -> None:
        pass  # TODO

    def gear_down(self) -> None:
        pass  # TODO


@dataclass
class Motor(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.MOTOR
    motor: ClassVar[MCP4161] = MCP4161()
    eco_status: bool = False

    def _setup(self) -> None:
        super()._setup()

    def _teardown(self) -> None:
        super()._teardown()

    def __update(self) -> None:
        while self.status:
            with self._environment.read_and_write() as data:
                gear_index_input_counter = data.gear_index_input_counter
                data.gear_index_input_counter = 0

            with self._environment.copy() as data:
                if data.battery_relay_status:
                    self.motor.state(True)
                    self.motor.direct(data.motor_direction_input)
                    self.motor.accelerate(data.acceleration_input)
                    self.motor.regenerate(data.regeneration_input)
                    self.motor.economize(data.eco_status_input)

                    while gear_index_input_counter > 0:
                        gear_index_input_counter -= 1
                        self.motor.gear_up()

                    while gear_index_input_counter < 0:
                        gear_index_input_counter += 1
                        self.motor.gear_down()
                else:
                    self.motor.state(False)
                    self.motor.direct(Direction.FORWARD)
                    self.motor.accelerate(0)
                    self.motor.regenerate(0)
                    self.motor.economize(False)
