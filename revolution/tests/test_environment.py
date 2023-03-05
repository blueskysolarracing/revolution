from queue import Empty
from unittest import TestCase, main

from revolution.environment import (
    Context,
    Endpoint,
    Environment,
    Header,
    Message,
)


class EnvironmentTestCase(TestCase):
    def test_receive_and_send(self) -> None:
        environment = Environment(Context())

        self.assertRaises(
            Empty,
            environment.receive_message,
            Endpoint.DEBUGGER,
            False,
        )
        self.assertRaises(
            Empty,
            environment.receive_message,
            Endpoint.DEBUGGER,
            timeout=0,
        )

        for i in range(3):
            environment.send_message(Endpoint.DEBUGGER, Message(Header.DEBUG))

        for i in range(3):
            self.assertEqual(
                environment.receive_message(Endpoint.DEBUGGER),
                Message(Header.DEBUG),
            )


if __name__ == '__main__':
    main()
