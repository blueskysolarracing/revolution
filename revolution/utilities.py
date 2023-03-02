from argparse import ArgumentParser, BooleanOptionalAction, Namespace
from code import interact
from datetime import datetime
from logging import DEBUG, INFO, basicConfig, getLogger
from sys import stderr
from threading import Thread

from revolution.application import Application
from revolution.environment import Context, Environment

_logger = getLogger(__name__)


def parse_arguments() -> Namespace:
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
        help='set debug mode (disabled by default)',
    )
    parser.add_argument(
        '-i',
        '--interactive',
        action=BooleanOptionalAction,
        help='set interactive mode (disabled by default)',
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    log_level = DEBUG if arguments.debug else INFO

    basicConfig(level=log_level, stream=stderr)
    _logger.info('Launching revolution...')

    context = Context()
    environment = Environment(context)
    threads = []

    for application_type in Application.__subclasses__():
        if application_type.endpoint is not None:
            threads.append(
                Thread(
                    target=application_type.main,
                    name=application_type.endpoint.name,
                    args=(environment,),
                ),
            )

    for thread in threads:
        thread.start()

    if arguments.interactive:
        interact(local={'environment': environment})

    for thread in threads:
        thread.join()
