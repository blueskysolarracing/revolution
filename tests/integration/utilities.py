from os import getuid
from pathlib import Path
from subprocess import PIPE, Popen

from posix_ipc import MessageQueue, O_CREAT, O_EXCL

PROJECT_PATH = Path(__file__).parent.parent.parent
TESTER_NAME = 'tester'


class ShellError(Exception):
    pass


def shell(*arguments):
    if not all(arguments):
        raise cls.ShellError('empty string argument passed')

    process = Popen(arguments, stdout=PIPE, stderr=PIPE)
    process.wait()
    stdout, stderr = process.communicate()

    if stderr:
        raise ShellError(stderr)

    return stdout.decode('utf-8')


def start():
    shell('sudo', str(PROJECT_PATH / 'start.sh'))


def stop():
    shell('sudo', str(PROJECT_PATH / 'stop.sh'))


class Message:
    __count = 0

    @classmethod
    def deserialize(cls, raw_message):
        tokens = raw_message.split('\0')

        assert not tokens[-1]

        (
            sender_name,
            receiver_name,
            header,
            *data,
            raw_priority,
            raw_identifier,
        ) = tokens[:-1]
        priority = int(raw_priority)
        identifier = int(raw_identifier)

        return cls(
            sender_name,
            receiver_name,
            header,
            data,
            priority,
            identifier,
        )

    def __init__(
            self,
            sender_name,
            receiver_name,
            header,
            data=(),
            priority=0,
            identifier=None,
    ):
        self.__sender_name = sender_name
        self.__receiver_name = receiver_name
        self.__header = header
        self.__data = tuple(data)
        self.__priority = priority

        if identifier is None:
            self.__identifier = self.__count
            self.__count += 1
        else:
            self.__identifier = identifier

    def __eq__(self, other):
        if not isinstance(other, Message):
            return NotImplemented

        return self.sender_name == other.sender_name \
            and self.receiver_name == other.receiver_name \
            and self.header == other.header \
            and self.data == other.data \
            and self.priority == other.priority \
            and self.identifier == other.identifier

    def __str__(self):
        return str(
            {
                'sender_name': self.sender_name,
                'receiver_name': self.receiver_name,
                'header': self.header,
                'data': self.data,
                'priority': self.priority,
                'identifier': self.identifier,
            },
        )

    @property
    def sender_name(self):
        return self.__sender_name

    @property
    def receiver_name(self):
        return self.__receiver_name

    @property
    def header(self):
        return self.__header

    @property
    def data(self):
        return self.__data

    @property
    def priority(self):
        return self.__priority

    @property
    def identifier(self):
        return self.__identifier

    def serialize(self):
        serialized_components = (
            self.__serialize(self.sender_name),
            self.__serialize(self.receiver_name),
            self.__serialize(self.header),
            *map(self.__serialize, self.data),
            self.__serialize(self.priority),
            self.__serialize(self.identifier),
        )

        return ''.join(serialized_components)

    def __serialize(self, component):
        return f'{component}\0'


class HeaderSpace:
    ABORT = "ABORT"
    DATA = "DATA"
    EXIT = "EXIT"
    RESPONSE = "RESPONSE"
    STATE = "STATE"
    STATUS = "STATUS"


class StateSpace:
    pass


class Topology:
    class Endpoint:
        def __init__(self, name):
            self.__name = name

        @property
        def name(self):
            return self.__name

        def send(
                self,
                header,
                data=(),
                priority=0,
                identifier=None,
                *,
                timeout=None,
                tester_name=TESTER_NAME,
        ):
            sender = MessageQueue(f'/{self.name}')
            message = Message(
                tester_name,
                self.name,
                header,
                data,
                priority,
                identifier,
            )

            sender.send(message.serialize(), timeout, priority)
            sender.close()

            return message

        def communicate(
                self,
                header,
                data=(),
                priority=0,
                identifier=None,
                *,
                timeout=None,
                tester_name=TESTER_NAME,
        ):
            receiver = MessageQueue(
                None if tester_name is None else f'/{tester_name}',
                O_CREAT | O_EXCL,
            )
            tester_name = receiver.name.lstrip('/')
            message = self.send(
                header,
                data,
                priority,
                identifier,
                timeout=timeout,
                tester_name=tester_name,
            )
            raw_message, _priority = receiver.receive(timeout)

            receiver.close()
            receiver.unlink()

            response = Message.deserialize(raw_message.decode('ascii'))

            assert response.sender_name == message.receiver_name
            assert response.receiver_name == message.sender_name
            assert response.header == HeaderSpace.RESPONSE
            assert response.priority == message.priority
            assert response.identifier == message.identifier

            return response

    DATABASE = Endpoint('database')
    REPLICA = Endpoint('replica')
    DISPLAY = Endpoint('display')
