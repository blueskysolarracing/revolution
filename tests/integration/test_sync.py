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
    @classmethod
    def setUpClass(cls):
        install()

    @classmethod
    def tearDownClass(cls):
        uninstall()

    def setUp(self):
        start()
        sleep(1)
        self.client = Client('client')

    def tearDown(self):
        stop()
        sleep(1)
        del self.client

    def test_marshal_write(self):
        state = {'Uno': 'One'}

        Topology.MARSHAL.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        state = {
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

        Topology.MARSHAL.reset_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        extra_state = {
            'One': 'Ichi',
            'Two': 'Ni',
        }

        Topology.MARSHAL.set_state(self.client, extra_state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state | extra_state,
            )

        Topology.MARSHAL.reset_state(self.client, {})

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), {})

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
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        delta = {
            'A': 'alpha',
            'B': 'beta',
            'C': 'theta',
            'D': 'gamma',
        }
        state |= delta

        Topology.REPLICA.set_state(self.client, delta)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        delta = {
            'O': 'Omega',
            'Z': 'zeta',
        }
        state |= delta

        Topology.TELEMETER.set_state(self.client, delta)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        state = {
            'A': 'A',
            'B': 'B',
            'C': 'C',
        }

        Topology.MISCELLANEOUS_CONTROLLER.reset_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        delta = {
            'Y': 'Y',
            'Z': 'Z',
        }
        state |= delta

        Topology.VOLTAGE_CONTROLLER.set_state(self.client, delta)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

    def test_mixed_write(self):
        state = {
            'Alexander': 'Scriabin',
            'Sergei': 'Rachmaninoff',
        }

        Topology.MARSHAL.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        extra_state = {
            'Alexander': 'Borodin',
        }

        Topology.POWER_SENSOR.set_state(self.client, extra_state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state | extra_state,
            )

        state = {
            'Anton': 'Webern',
        }

        Topology.DISPLAY_DRIVER.reset_state(self.client, state)
        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        state = {
            'Franz': 'Liszt',
            'Charles-Valentin': 'Alkan',
            'Frederic': 'Chopin',
        }

        Topology.REPLICA.reset_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        extra_state = {
            'Dmitri': 'Shostakovich',
            'Sergei': 'Prokofiev',
            'Nikolai': 'Medtner',
        }

        Topology.MARSHAL.set_state(self.client, extra_state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state | extra_state,
            )

        extra_state |= {
            'Maurice': 'Ravel',
            'Claude': 'Debussy',
            'Felix': 'Mendelssohn',
            'Camille': 'Saint-Saens',
            'Kaikhorsru': 'Sorabji',
        }

        Topology.MOTOR_CONTROLLER.set_state(self.client, extra_state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state | extra_state,
            )


if __name__ == '__main__':
    main()
