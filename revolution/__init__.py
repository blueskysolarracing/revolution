"""Revolution is the software for the next generation electrical system
for Blue Sky Solar Racing.

Basic usage:

.. code-block:: sh

   python -m revolution

Print help:

.. code-block:: sh

   python -m revolution --help

Enable debug mode:

.. code-block:: sh

   python -m revolution --debug

Enable interactive mode:

.. code-block:: sh

   python -m revolution --interactive
"""

__all__ = (
    '__author__',
    '__author_email__',
    '__classifiers__',
    '__description__',
    '__install_requires__',
    '__keywords__',
    '__license__',
    '__long_description__',
    '__long_description_content_type__',
    '__package_data__',
    '__packages__',
    '__project_urls__',
    '__python_requires__',
    '__title__',
    '__url__',
    '__version__',
    'ADC78H89',
    'Application',
    'Context',
    'DataAccessor',
    'DataManager',
    'Direction',
    'DirectionalPad',
    'Display',
    'Endpoint',
    'Environment',
    'Header',
    'M2096',
    'Message',
    'Miscellaneous',
    'Motor',
    'SteeringWheel',
    'WorkerPool',
    'main',
    'parse_arguments',
)

from revolution.application import Application
from revolution.data import DataAccessor, DataManager
from revolution.display import Display
from revolution.drivers import ADC78H89, M2096
from revolution.environment import (
    Context,
    Direction,
    DirectionalPad,
    Endpoint,
    Environment,
    Header,
    Message,
)
from revolution.miscellaneous import Miscellaneous
from revolution.motor import Motor
from revolution.steering_wheel import SteeringWheel
from revolution.utilities import main, parse_arguments
from revolution.worker_pool import WorkerPool

__title__ str = 'blueskysolarracing-revolution'
__version__: str = '0.0.0.dev1'
__description__: str \
    = 'Software for the Blue Sky Solar Racing Gen 12 electrical system'
__long_description__: str = __doc__
__long_description_content_type__: str = 'text/x-rst'
__author__: str = 'Blue Sky Solar Racing'
__author_email__: str = 'blueskysolar@studentorg.utoronto.ca'
__url__: str = 'https://github.com/blueskysolarracing/revolution'
__packages__: str = 'revolution'
__package_data__: dict[str, str] = {'revolution': 'py.typed'}
__classifiers__: tuple[str, ...] = (
    'Topic :: Education',
    'License :: OSI Approved :: GNU Affero General Public License v3',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
)
__license__: str = 'AGPLv3'
__keywords__: tuple[str, ...] = 'blueskysolarracing', 'solar', 'car', 'toradex'
__project_urls__: dict[str, str] = {
    'Documentation': 'https://bssr-revolution.readthedocs.io/en/latest/',
    'Source': 'https://github.com/blueskysolarracing/revolution',
    'Tracker': 'https://github.com/blueskysolarracing/revolution/issues',
}
__install_requires__: str = 'python-periphery~=2.3.0'
__python_requires__: str = '>=3.10'
