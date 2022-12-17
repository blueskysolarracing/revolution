from random import choice
from time import sleep
from unittest import TestCase, main

from utilities import HeaderSpace, Topology, start, stop


class SyncTestCase(TestCase):
    TIMEOUT = 1

    def setUp(self):
        start()
        sleep(self.TIMEOUT)

    def tearDown(self):
        stop()
        sleep(self.TIMEOUT)

    def get_state(self, key, priority=0, identifier=None, *, timeout=None):
        response = Topology.DATABASE.communicate(
            HeaderSpace.STATE,
            (key,),
            priority,
            identifier,
            timeout=timeout,
        )
        value = response.data[0] if response.data else None

        self.assertEqual(response.sender_name, Topology.DATABASE.name)
        self.assertEqual(response.header, HeaderSpace.RESPONSE)
        self.assertSequenceEqual(
            response.data,
            () if value is None else (value,),
        )
        self.assertEqual(response.priority, priority)

        if identifier is not None:
            self.assertEqual(response.identifier, identifier)

        return value

    def set_state(
            self,
            key,
            value,
            priority=0,
            identifier=None,
            *,
            timeout=None,
    ):
        response = Topology.DATABASE.communicate(
            HeaderSpace.STATE,
            (key, value),
            priority,
            identifier,
            timeout=timeout,
        )

        self.assertEqual(response.sender_name, Topology.DATABASE.name)
        self.assertEqual(response.header, HeaderSpace.RESPONSE)
        self.assertSequenceEqual(response.data, ())
        self.assertEqual(response.priority, priority)

        if identifier is not None:
            self.assertEqual(response.identifier, identifier)

    def get_states(
            self,
            keys,
            priority=0,
            identifier=None,
            *,
            timeout=None,
    ):
        states = {}

        for key in keys:
            states[key] = self.get_state(
                key,
                priority,
                identifier,
                timeout=timeout,
            )

        return states

    def set_states(
            self,
            states,
            priority=0,
            identifier=None,
            *,
            timeout=None,
    ):
        for key, value in states.items():
            self.set_state(key, value, priority, identifier, timeout=timeout)

    def test_read_write(self):
        states = {
            'Sergei': 'Rachmaninoff',
            'Alexander': 'Scriabin',
            'Ludwig Van': 'Beethoven',
            'Frederich': 'Chopin',
        }

        self.set_states(states)
        self.assertDictEqual(self.get_states(states.keys()), states)

        sub_states = {
            'Wolfgang Amadeus': 'Mozart',
            'Johann Sebastian': 'Bach',
        }
        states |= sub_states

        self.set_states(sub_states)
        self.assertDictEqual(self.get_states(states.keys()), states)

    def test_failures(self):
        states = {
            'Takina': 'Inoue',
            'Chisato': 'Nishikigi',
            'Kurumi': '',
        }

        self.set_states(states)
        self.assertDictEqual(self.get_states(states.keys()), states)

        sleep(self.TIMEOUT)
        Topology.DATABASE.send(HeaderSpace.ABORT)
        sleep(self.TIMEOUT)
        self.assertDictEqual(self.get_states(states.keys()), states)

        sleep(self.TIMEOUT)
        Topology.REPLICA.send(HeaderSpace.ABORT)
        sleep(self.TIMEOUT)
        self.assertDictEqual(self.get_states(states.keys()), states)

        states = {
            'Takina': None,
            'Chisato': None,
            'Kurumi': None,
        }

        sleep(self.TIMEOUT)
        Topology.REPLICA.send(HeaderSpace.ABORT)
        Topology.DATABASE.send(HeaderSpace.ABORT)
        sleep(self.TIMEOUT)
        self.assertDictEqual(self.get_states(states.keys()), states)


if __name__ == '__main__':
    main()
