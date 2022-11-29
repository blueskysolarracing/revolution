from random import choice
from time import sleep
from unittest import TestCase, main

from tests.integration.utilities import (
    Client,
    Topology,
    install,
    start,
    stop,
    uninstall,
)


class SyncTestCase(TestCase):
    TIMEOUT = 1

    @classmethod
    def setUpClass(cls):
        install()

    @classmethod
    def tearDownClass(cls):
        uninstall()

    def setUp(self):
        start()
        sleep(self.TIMEOUT)
        self.client = Client('client')

    def tearDown(self):
        stop()
        sleep(self.TIMEOUT)
        del self.client

    def test_marshal_write(self):
        state = {'Uno': 'One'}

        Topology.MARSHAL.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

        state |= {
            'Zero': '0',
            'One': '1',
            'Two': '2',
            'Three': '3',
            'Four': '4',
            'Five': '5',
            'Six': '6',
            'Seven': '7',
            'Eight': '8',
            'Nine': '9',
        }

        Topology.MARSHAL.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

        extra_state = {
            'One': 'Ichi',
            'Two': 'Ni',
        }
        state |= extra_state

        Topology.MARSHAL.set_state(self.client, extra_state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

        Topology.MARSHAL.set_state(self.client, {})

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

    def test_soldier_write(self):
        state = {
            'A': 'a',
            'B': 'b',
            'C': 'c',
            'D': 'd',
            'E': 'e',
            'F': 'f',
        }

        Topology.REPLICA.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

        extra_state = {
            'A': 'alpha',
            'B': 'beta',
            'C': 'theta',
            'D': 'gamma',
        }
        state |= extra_state

        Topology.REPLICA.set_state(self.client, extra_state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

        extra_state = {
            'O': 'Omega',
            'Z': 'zeta',
        }
        state |= extra_state

        Topology.TELEMETER.set_state(self.client, extra_state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

        state |= {
            'A': 'A',
            'B': 'B',
            'C': 'C',
        }

        Topology.MISCELLANEOUS_CONTROLLER.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

        extra_state = {
            'Y': 'Y',
            'Z': 'Z',
        }
        state |= extra_state

        Topology.VOLTAGE_CONTROLLER.set_state(self.client, extra_state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

    def test_mixed_write(self):
        state = {
            'Alexander': 'Scriabin',
            'Sergei': 'Rachmaninoff',
        }

        Topology.MARSHAL.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

        extra_state = {
            'Alexander': 'Borodin',
        }
        state |= extra_state

        Topology.POWER_SENSOR.set_state(self.client, extra_state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

        extra_state = {
            'Anton': 'Webern',
        }
        state |= extra_state

        Topology.DISPLAY_DRIVER.set_state(self.client, extra_state)
        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

        state |= {
            'Franz': 'Liszt',
            'Charles-Valentin': 'Alkan',
            'Frederic': 'Chopin',
        }

        Topology.REPLICA.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

        extra_state = {
            'Dmitri': 'Shostakovich',
            'Sergei': 'Prokofiev',
            'Nikolai': 'Medtner',
        }
        state |= extra_state

        Topology.MARSHAL.set_state(self.client, extra_state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

        extra_state |= {
            'Maurice': 'Ravel',
            'Claude': 'Debussy',
            'Felix': 'Mendelssohn',
            'Camille': 'Saint-Saens',
            'Kaikhorsru': 'Sorabji',
        }
        state |= extra_state

        Topology.MOTOR_CONTROLLER.set_state(self.client, extra_state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), state)

    def test_random_update(self):
        count = 100
        key = 'voice'
        values = 'dub', 'sub'
        state = None

        for _ in range(count):
            endpoint = choice(Topology.get_endpoints())
            value = choice(values)
            state = {key: value}
            endpoint.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertEqual(endpoint.get_state(self.client), state)

    def test_write(self):
        count = 100

        for i in range(count):
            endpoint = choice(Topology.get_endpoints())
            endpoint.set_state(self.client, {str(i): str(i)})

        state = dict(zip(map(str, range(count)), map(str, range(count))))

        for endpoint in Topology.get_endpoints():
            self.assertEqual(endpoint.get_state(self.client), state)


if __name__ == '__main__':
    main()
