from dataclasses import dataclass
from multiprocessing import get_logger
from typing import ClassVar

from revolution.application import Application
from revolution.environment import Endpoint

_logger = get_logger()


@dataclass
class Display(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.DISPLAY

    pass  # TODO
