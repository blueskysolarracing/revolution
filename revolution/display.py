from dataclasses import dataclass
from multiprocessing import get_logger

from revolution.application import Application
from revolution.environment import Endpoint

_logger = get_logger()


@dataclass
class Display(Application):
    endpoint = Endpoint.DISPLAY

    pass  # TODO