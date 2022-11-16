from collections import deque
from os import geteuid
from pathlib import Path
from subprocess import Popen, PIPE

PROJECT_PATH = Path(__file__).parent.parent.parent


def shell(*arguments):
    if not all(arguments):
        raise ShellError('empty string argument passed')

    process = Popen(arguments, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    if stderr:
        raise ShellError(stderr)

    return stdout.decode('utf-8')


def install():
    shell('sudo', str(PROJECT_PATH / 'install.sh'))


def start():
    shell('sudo', str(PROJECT_PATH / 'start.sh'))


def stop():
    shell('sudo', str(PROJECT_PATH / 'stop.sh'))


def uninstall():
    shell('sudo', str(PROJECT_PATH / 'uninstall.sh'))


def unlink(*names):
    shell('sudo', str(PROJECT_PATH / 'src' / 'unlinker'), *names)


class ShellError(Exception):
    pass


class Topology:
    class Endpoint:
        def __init__(self, name):
            self.__name = name

        @property
        def name(self):
            return self.__name

        def abort(self, client):
            client.send(self.name, 'ABORT')

        def exit(self, client):
            client.send(self.name, 'EXIT')

        def set_state(self, client, state):
            client.send(self.name, 'SET', *self.__flatten(state))

        def reset_state(self, client, state):
            client.send(self.name, 'RESET', *self.__flatten(state))

        def get_state(self, client):
            raw_data = client.send(self.name, 'GET')

            if raw_data is None:
                return None

            data = raw_data.split()[4:-2]

            return dict(zip(data[::2], data[1::2]))

        @classmethod
        def __flatten(cls, state):
            arguments = []

            for key, value in zip(state.keys(), state.values()):
                arguments.append(key)
                arguments.append(value)

            return arguments

    MARSHAL = Endpoint('marshal')
    DISPLAY_DRIVER = Endpoint('display_driver')
    MISCELLANEOUS_CONTROLLER = Endpoint('miscellaneous_controller')
    MOTOR_CONTROLLER = Endpoint('motor_controller')
    POWER_SENSOR = Endpoint('power_sensor')
    REPLICA = Endpoint('replica')
    TELEMETER = Endpoint('telemeter')
    VOLTAGE_CONTROLLER = Endpoint('voltage_controller')

    @classmethod
    def get_endpoints(cls):
        return (
            cls.MARSHAL,
            cls.DISPLAY_DRIVER,
            cls.MISCELLANEOUS_CONTROLLER,
            cls.MOTOR_CONTROLLER,
            cls.POWER_SENSOR,
            cls.REPLICA,
            cls.TELEMETER,
            cls.VOLTAGE_CONTROLLER,
        )


class Client:
    PATH = PROJECT_PATH / 'src' / 'client'

    def __init__(self, name):
        if not name:
            raise ValueError('name is an empty string')

        self.__name = name
        self.__raw_messages = deque()

    def __del__(self):
        unlink(self.name)

    @property
    def name(self):
        return self.__name

    def receive(self):
        return self.__process(shell(str(self.PATH), self.name))

    def send(self, recipient_name, header, *data):
        return self.__process(
            shell(str(self.PATH), self.name, recipient_name, header, *data),
        )

    def __process(self, stdout):
        for raw_message in filter(None, map(str.strip, stdout.split('\n'))):
            self.__raw_messages.append(raw_message)

        return self.__raw_messages.popleft() if self.__raw_messages else None
