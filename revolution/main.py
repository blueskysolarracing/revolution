from argparse import ArgumentParser, BooleanOptionalAction, Namespace
from code import interact
from datetime import datetime
from logging import basicConfig, DEBUG, getLogger, INFO
from sys import stderr
from threading import Thread
from typing import Any

from door.threading2 import AcquirableDoor

from revolution.environment import Environment

_logger = getLogger(__name__)


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
        '-f',
        '--file',
        help='file mode (disabled by default)',
        nargs=1,
    )
    parser.add_argument(
        '-i',
        '--interactive',
        action=BooleanOptionalAction,
        help='interactive mode (disabled by default)',
    )

    return parser.parse_args()


def main(configurations: Any) -> None:
    args = parse_args()
    log_level = DEBUG if args.debug else INFO

    basicConfig(level=log_level, stream=stderr)
    _logger.info('Launching revolution...')

    environment = Environment(
        AcquirableDoor(configurations.CONTEXTS),
        configurations.PERIPHERIES,
        configurations.SETTINGS,
    )
    threads = []

    for application_type in configurations.APPLICATION_TYPES:
        thread = Thread(target=application_type.main, args=(environment,))

        threads.append(thread)

    for thread in threads:
        thread.start()

    if args.file:
        content = open(args.file[0]).read()

        exec(content, locals={'environment': environment})

    if args.interactive:
        interact(local={'environment': environment})

    for thread in threads:
        thread.join()
