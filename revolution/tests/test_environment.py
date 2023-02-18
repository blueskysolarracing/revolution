from queue import Empty
from typing import cast
from unittest import TestCase, main

from revolution.environment import (
    Context,
    Endpoint,
    Environment,
    Message,
)


class EnvironmentTestCase(TestCase):
    def test_receive_and_send(self) -> None:
        environment = Environment(Context())

        self.assertRaises(Empty, environment.receive, Endpoint.DEBUGGER, False)
        self.assertRaises(
            Empty,
            environment.receive,
            Endpoint.DEBUGGER,
            timeout=0,
        )

        for i in range(3):
            environment.send(Endpoint.DEBUGGER, cast(Message, i))

        for i in range(3):
            self.assertEqual(environment.receive(Endpoint.DEBUGGER), i)


if __name__ == '__main__':
    main()
