==========
Revolution
==========

Revolution is the software for the next generation electrical system
for Blue Sky Solar Racing.

Project Setup
=============

In project root directory, create a Python virtual environment.

.. code-block:: sh

   python -m venv venv

Activate the Python virtual environment.

.. code-block:: sh

   source venv/bin/activate

Install the project requirements.

.. code-block:: sh

   pip install -r requirements.txt

Code Style and Static Type Checking
===================================

Run style checker.

.. code-block:: sh

   flake8 revolution configurations.py

Run static type checker.

.. code-block:: sh

   mypy --strict revolution configurations.py

Unit and Documentation Testing
==============================

Run unit tests.

.. code-block:: sh

   export REVOLUTION_CONFIGURATIONS_MODULE=revolution.tests.configurations
   python -m unittest

Above is equivalent to below...

.. code-block:: sh

   REVOLUTION_CONFIGURATIONS_MODULE=revolution.tests.configurations python -m unittest

Run documentation tests.

.. code-block:: sh

   export REVOLUTION_CONFIGURATIONS_MODULE=revolution.tests.configurations
   python -m doctest revolution/*.py

Above is equivalent to below...

.. code-block:: sh

   REVOLUTION_CONFIGURATIONS_MODULE=revolution.tests.configurations python -m doctest revolution/*.py

Project Deployment
==================

Make sure all version occurrences have been updated.

Tag the release version.

.. code-block:: sh

   git tag v<version>

Build the docker image.

.. code-block:: sh

   docker build -t blueskysolarracing/revolution:<version> .

Push the docker image.

.. code-block:: sh

   docker push blueskysolarracing/revolution:<version>

In deployment platform, pull the docker image and run as a docker
container in detached mode.

.. code-block:: sh

   docker run -d -v /dev:/dev -v /sys/class/pwm:/sys/class/pwm blueskysolarracing/revolution:<version>
