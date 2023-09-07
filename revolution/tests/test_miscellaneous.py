from threading import Thread
from unittest import main, TestCase
from unittest.mock import MagicMock

from revolution.environment import Context, Environment, Header, Message
from revolution.miscellaneous import Miscellaneous


class MiscellaneousTestCase(TestCase):
    def test_update(self) -> None:
        context = Context()
        environment = Environment(context)
        miscellaneous \
            = Miscellaneous(environment, *(MagicMock() for _ in range(7)))
        thread = Thread(target=miscellaneous.mainloop)

        thread.start()

        # TODO

        environment.send_message(miscellaneous.endpoint, Message(Header.STOP))
        thread.join()


if __name__ == '__main__':
    main()
