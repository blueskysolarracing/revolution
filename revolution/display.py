from dataclasses import dataclass
from logging import getLogger
from typing import ClassVar

from revolution.application import Application
from revolution.environment import Endpoint

_logger = getLogger(__name__)


@dataclass
class Display(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.DISPLAY

    # display design based on google slides that you can find here
    # https://docs.google.com/presentation/d/1P_kAPFkVbpgUW_R5nXAC8cFNGyiidCfmwuXg6XJ8BWc/edit?usp=sharing

    # instantiate the two object for two display and run init for controller
    def __post_init__(self) -> None:
        pass  # TODO

    # draw blue sky logo, wait for a while, then draw the default screen
    def startup(self) -> None:
        pass  # TODO

    # draw display
    def draw(self, choice: int, flags: int, debug: bool) -> None:
        if debug:
            self.debug()
        else:
            self.drawD1()
            self.drawD2(choice, flags)

    # D1 only needs one cause it always show the same thing
    def drawD1(self) -> None:
        pass  # TODO

    # D2 will choose what to draw depending on driver choices (choice)
    # or the fault screens (flags)
    def drawD2(self, choice: int, flags: int) -> None:
        if flags:
            match flags:
                case 0:
                    self.cruiseActivate()
                case 1:
                    self.cruiseDeactivate()
                case 2:
                    self.ignitionOff()
                case 3:
                    self.bmsFault()
                case _:
                    self.youFuckedUp()
        else:
            match choice:
                case 0:
                    self.default()
                case 1:
                    self.lowVolt()
                case 2:
                    self.detailed()
                case 3:
                    self.status()
                case _:
                    self.youFuckedUp()

    # drawing funcions for D2
    def default(self) -> None:
        pass  # TODO

    def lowVolt(self) -> None:
        pass  # TODO

    def detailed(self) -> None:
        pass  # TODO

    def status(self) -> None:
        pass  # TODO

    def cruiseActivate(self) -> None:
        pass  # TODO

    def cruiseDeactivate(self) -> None:
        pass  # TODO

    def ignitionOff(self) -> None:
        pass  # TODO

    def bmsFault(self) -> None:
        pass  # TODO

    def debug(self) -> None:
        pass  # TODO

    def youFuckedUp(self) -> None:
        pass  # TODO

    pass  # TODO
