from argparse import ArgumentParser, BooleanOptionalAction, Namespace
from code import interact
from datetime import datetime
from logging import basicConfig, DEBUG, getLogger, INFO
from sys import stderr
from threading import Thread

from revolution.application import Application
from revolution.contexts import Contexts
from revolution.data import DataManager
from revolution.debugger import Debugger
from revolution.display import Display
from revolution.environment import Environment
from revolution.miscellaneous import Miscellaneous
from revolution.motor import Motor
from revolution.peripheries import Peripheries
from revolution.power import Power
from revolution.settings import Settings
from revolution.steering_wheel import SteeringWheel
from revolution.telemeter import Telemeter

_logger = getLogger(__name__)
APPLICATION_TYPES: tuple[type[Application], ...] = (
    Debugger,
    Display,
    Miscellaneous,
    Motor,
    Power,
    SteeringWheel,
    Telemeter,
)


def parse_args() -> Namespace:
    parser = ArgumentParser(
        prog='Revolution',
        description='Software for the Blue Sky Solar Racing Gen 12 electrical '
                    'system',
        epilog=f'Copyright (c) {datetime.now().year} - Blue Sky Solar Racing',
    )

    parser.add_argument(
        '-d',
        '--debug',
        action=BooleanOptionalAction,
        help='debug mode (disabled by default)',
    )
    parser.add_argument(
        '-i',
        '--interactive',
        action=BooleanOptionalAction,
        help='interactive mode (disabled by default)',
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    log_level = DEBUG if args.debug else INFO

    basicConfig(level=log_level, stream=stderr)
    _logger.info('Launching revolution...')

    contexts = Contexts()
    peripheries = Peripheries()
    settings = Settings()
    environment = Environment(DataManager(contexts), peripheries, settings)
    threads = []

    for application_type in APPLICATION_TYPES:
        thread = Thread(target=application_type.main, args=(environment,))

        threads.append(thread)

    for thread in threads:
        thread.start()

    if args.interactive:
        interact(local={'environment': environment})

    for thread in threads:
        thread.join()
