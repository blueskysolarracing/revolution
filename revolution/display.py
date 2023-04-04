from dataclasses import dataclass, field
from logging import getLogger
from typing import ClassVar

from revolution.application import Application
from revolution.environment import Endpoint

import st7565  # type:ignore
import xglcd_font as font  # type:ignore

_logger = getLogger(__name__)


@dataclass
class Display(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.DISPLAY
    d1: st7565.Glcd = field(init=False)
    d2: st7565.Glcd = field(init=False)
    JetBrains13x20: font.XglcdFont = field(init=False)
    JetBrains13x21: font.XglcdFont = field(init=False)
    Font5x7: font.XglcdFont = field(init=False)
    Liberation_Sans20x28: font.XglcdFont = field(init=False)

    # display design based on google slides that you can find here
    # https://docs.google.com/presentation/d/1P_kAPFkVbpgUW_R5nXAC8cFNGyiidCfmwuXg6XJ8BWc/edit?usp=sharing

    # instantiate the two object for two display and run init for controller
    # also create Font object to later write with
    def __post_init__(self) -> None:
        self.d1 = st7565.Glcd()
        self.d2 = st7565.Glcd()
        self.d1.init()
        self.d2.init()
        self.JetBrains13x20 = font.XglcdFont("display_data/JetBrains_Mono13x20.c", 13, 20, 97)  # noqa: E501
        self.JetBrains13x21 = font.XglcdFont("display_data/JetBrains_Mono13x21_Symbol.c", 13, 21, 32)  # noqa: E501
        self.Liberation_Sans20x28 = font.XglcdFont("revolution/display_data/Liberation_Sans20x28_Numbers.c", 20, 28, 46)  # noqa: E501
        self.Font5x7 = font.XglcdFont("display_data/font5x7.c", 5, 7, 32)

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
