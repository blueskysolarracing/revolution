from importlib import import_module
from os import getenv

from revolution.main import main

configurations_module = getenv('REVOLUTION_CONFIGURATIONS_MODULE')

if configurations_module is None:
    raise ValueError(
        'configurations module not set as an environment variable '
        '(ex: \'REVOLUTION_CONFIGURATIONS_MODULE=configurations\')'
    )

configurations = import_module(configurations_module)

if __name__ == '__main__':
    main(configurations)
