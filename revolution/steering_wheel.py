from dataclasses import dataclass
from multiprocessing import get_logger

from revolution.application import Application
from revolution.environment import Endpoint

_logger = get_logger()


@dataclass
class SteeringWheel(Application):
    endpoint = Endpoint.STEERING_WHEEL

    def _setup(self) -> None:
        pass
