from argparse import ArgumentParser, BooleanOptionalAction, Namespace
from code import interact
from datetime import datetime
from logging import DEBUG, INFO, basicConfig, getLogger
from sys import stderr

from revolution.application import Application
from revolution.environment import Context, Environment
from revolution.thread_pool import ThreadPool

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
    thread_pool = ThreadPool()

    for application_type in Application.__subclasses__():
        if application_type.endpoint is not None:
            thread_pool.add(application_type.main, environment)

    if arguments.interactive:
        interact(local={'environment': environment})

    thread_pool.join()
