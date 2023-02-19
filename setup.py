#!/usr/bin/env python3

from distutils.core import setup

with open('README.rst', 'r') as file:
    long_description = file.read()

setup(
    name='blueskysolarracing-revolution',
    version='0.0.0.dev0',
    description='Software for the Blue Sky Solar Racing Gen 12 electrical '
                'system',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Blue Sky Solar Racing',
    author_email='juho-kim@outlook.com',
    url='https://github.com/blueskysolarracing/revolution',
    packages=['revolution'],
    package_data={'revolution': ['py.typed']},
    classifiers=[
        'Topic :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    license='AGPLv3',
    keywords=['blueskysolarracing', 'solar', 'car', 'toradex'],
    project_urls={
        'Documentation': 'https://bssr-revolution.readthedocs.io/en/latest/',
        'Source': 'https://github.com/blueskysolarracing/revolution',
        'Tracker': 'https://github.com/blueskysolarracing/revolution/issues',
    },
    install_requires=[
        'gpiod~=1.5.3',
        'spidev~=3.6',
        'python-periphery~=2.3.0',
    ],
    python_requires='>=3.10',
)
