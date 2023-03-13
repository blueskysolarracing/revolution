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

   flake8 revolution

Run static type checker.

.. code-block:: sh

   mypy --strict revolution

Unit and Documentation Testing
==============================

Run unit tests.

.. code-block:: sh

   python -m unittest

Run documentation tests.

.. code-block:: sh

   python -m doctest revolution/*.py

Project Deployment
==================

Make sure all version occurrences have been updated.

Tag the release version.

.. code-block:: sh

   git tag v<version>

Build the project.

.. code-block:: sh

   python -m build

Upload the packages.

.. code-block:: sh

   twine upload dist/*

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

Debugging
=========

The debug Dockerfile is different from the production Dockerfile as it
utilizes the code from the host machine through bind mount and runs
Revolution with debug and interactive mode enabled.

Build the debug docker image.

.. code-block:: sh

   docker build -f debug.Dockerfile -t blueskysolarracing/revolution:debug .

Run the debug docker image.

.. code-block:: sh

   docker run -i -v /dev:/dev -v /sys/class/pwm:/sys/class/pwm -v .:/usr/src/revolution blueskysolarracing/revolution:debug
