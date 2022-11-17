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


class FailoverTestCase(TestCase):
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

    def test_marshal_failover(self):
        s0 = {
            'Takina': 'Inoue',
            'Chisato': 'Nishikigi',
            'Kurumi': 'Walnut',
        }

        Topology.DISPLAY_DRIVER.set_state(self.client, s0)

        s1 = {
            'Cafe': 'LycoReco',
            'Alan': 'Institute',
            'Direct': 'Attack',
        }

        Topology.MARSHAL.set_state(self.client, s1)

        s2 = {
            'Lycoris': 'Recoil',
        }

        Topology.REPLICA.set_state(self.client, s2)

        state = s0 | s1 | s2

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        Topology.MARSHAL.abort(self.client)
        sleep(1)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        Topology.MARSHAL.exit(self.client)

        for endpoint in Topology.get_endpoints():
            if endpoint == Topology.MARSHAL:
                self.assertIsNone(endpoint.get_state(self.client))
            else:
                self.assertDictEqual(
                    endpoint.get_state(self.client),
                    state,
                )

        start()
        sleep(1)

        self.client.receive()

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

    def test_replica_failover(self):
        state = {
            'Joe': 'Biden',
            'Donald': 'Trump',
            'Barack': 'Obama',
            'George': 'Bush',
            'Bill': 'Clinton',
        }

        Topology.MARSHAL.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        Topology.REPLICA.abort(self.client)
        sleep(1)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        Topology.REPLICA.exit(self.client)

        for endpoint in Topology.get_endpoints():
            if endpoint == Topology.REPLICA:
                self.assertIsNone(endpoint.get_state(self.client))
            else:
                self.assertDictEqual(
                    endpoint.get_state(self.client),
                    state,
                )

        start()
        sleep(1)

        self.client.receive()

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

    def test_non_replica_soldier_failover(self):
        s0 = {
            'Vladimir': 'Putin',
            'Kim': 'Jong-un',
            'Xi': 'Jinping',
            'Bashar': 'al-Assad',
            'Ruhollah': 'Khomeini',
        }

        Topology.MARSHAL.set_state(self.client, s0)

        s1 = {
            'Bin': 'Laden',
            'Alexander': 'Lukashenko',
            'Fidel': 'Castro',
            'Daniel': 'Ortega',
            'Nicolas': 'Maduro',
        }

        Topology.MARSHAL.set_state(self.client, s1)

        state = s0 | s1

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        Topology.DISPLAY_DRIVER.abort(self.client)
        sleep(1)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        Topology.DISPLAY_DRIVER.exit(self.client)

        for endpoint in Topology.get_endpoints():
            if endpoint == Topology.DISPLAY_DRIVER:
                self.assertIsNone(endpoint.get_state(self.client))
            else:
                self.assertDictEqual(
                    endpoint.get_state(self.client),
                    state,
                )

        start()
        sleep(1)

        self.client.receive()

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

    def test_non_replica_soldiers_failover(self):
        state = {
            'Hitagi': 'Crab',
            'Mayoi': 'Snail',
            'Suruga': 'Monkey',
            'Nadeko': 'Snake',
            'Tsubasa': 'Cat',
            'Karen': 'Bee',
            'Tsukihi': 'Phoenix',
        }

        Topology.MARSHAL.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        for endpoint in Topology.get_endpoints():
            if endpoint != Topology.MARSHAL \
                    and endpoint != Topology.REPLICA:
                endpoint.abort(self.client)

        sleep(1)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        for endpoint in Topology.get_endpoints():
            if endpoint != Topology.MARSHAL \
                    and endpoint != Topology.REPLICA:
                endpoint.exit(self.client)

        for endpoint in Topology.get_endpoints():
            if endpoint != Topology.MARSHAL \
                    and endpoint != Topology.REPLICA:
                self.assertIsNone(endpoint.get_state(self.client))
            else:
                self.assertDictEqual(
                    endpoint.get_state(self.client),
                    state,
                )

        start()
        sleep(1)

        for endpoint in Topology.get_endpoints():
            if endpoint != Topology.MARSHAL \
                    and endpoint != Topology.REPLICA:
                self.client.receive()

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

    def test_master_and_non_replica_soldiers_failover(self):
        state = {
            'Tsubasa': 'Family',
            'Mayoi': 'Jiangshi',
            'Suruga': 'Devil',
            'Nadeko': 'Medusa',
            'Shinobu': 'Time',
            'Hitagi': 'End',
            'Yotsugi': 'Doll',
        }

        Topology.MARSHAL.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        for endpoint in Topology.get_endpoints():
            if endpoint != Topology.REPLICA:
                endpoint.abort(self.client)

        sleep(1)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        for endpoint in Topology.get_endpoints():
            if endpoint != Topology.REPLICA:
                endpoint.exit(self.client)

        for endpoint in Topology.get_endpoints():
            if endpoint != Topology.REPLICA:
                self.assertIsNone(endpoint.get_state(self.client))
            else:
                self.assertDictEqual(
                    endpoint.get_state(self.client),
                    state,
                )

        start()
        sleep(1)

        for endpoint in Topology.get_endpoints():
            if endpoint != Topology.REPLICA:
                self.client.receive()

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

    def test_master_and_replica_failover(self):
        state = {
            'Ougi': 'Formula',
            'Sodachi': 'Riddle',
            'Sodachi': 'Lost',
            'Shinobu': 'Mail',
            'Mayoi': 'Hello',
            'Hitagi': 'Rendezvous',
            'Ougi': 'Dark',
        }

        Topology.MARSHAL.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        Topology.MARSHAL.abort(self.client)
        Topology.REPLICA.abort(self.client)
        sleep(1)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), {})

        Topology.MARSHAL.set_state(self.client, state)

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(
                endpoint.get_state(self.client),
                state,
            )

        Topology.MARSHAL.exit(self.client)
        Topology.REPLICA.exit(self.client)

        for endpoint in Topology.get_endpoints():
            if endpoint == Topology.MARSHAL \
                    or endpoint == Topology.REPLICA:
                self.assertIsNone(endpoint.get_state(self.client))
            else:
                self.assertDictEqual(
                    endpoint.get_state(self.client),
                    state,
                )

        start()
        sleep(1)

        self.client.receive()
        self.client.receive()

        for endpoint in Topology.get_endpoints():
            self.assertDictEqual(endpoint.get_state(self.client), {})


if __name__ == '__main__':
    main()
