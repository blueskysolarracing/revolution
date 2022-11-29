from unittest import TestCase, main

from tests.integration.utilities import Client


class ClientTestCase(TestCase):
    CLIENT_COUNT = 8

    def setUp(self):
        self.clients = []

        for i in range(self.CLIENT_COUNT):
            self.clients.append(Client(f'client-{i}'))

    def tearDown(self):
        del self.clients

    def test_receive(self):
        recipients = self.clients[1:]
        sender = self.clients[0]
        header = 'HEADER'
        raw_data = 'To be or not to be, that is the question:'
        data = raw_data.split()
        content = f'{header} {len(data)} {raw_data} 0 0'

        for recipient in recipients:
            self.assertIsNone(recipient.receive())
            self.assertIsNone(sender.send(recipient.name, header, *data))
            self.assertEqual(
                recipient.receive(),
                f'{sender.name} {recipient.name} {content}',
            )
            self.assertIsNone(recipient.receive())

    def test_send(self):
        recipient = self.clients[0]
        senders = self.clients[1:]
        header = 'HEADER'
        raw_data = 'To be or not to be, that is the question:'
        data = raw_data.split()
        content = f'{header} {len(data)} {raw_data} 0 0'

        for sender in senders:
            self.assertIsNone(recipient.receive())
            self.assertIsNone(sender.send(recipient.name, header, *data))
            self.assertEqual(
                recipient.receive(),
                f'{sender.name} {recipient.name} {content}',
            )
            self.assertIsNone(recipient.receive())

    def test_chained_communication(self):
        header = 'Blue'
        raw_data = 'Sky Solar Racing'
        data = raw_data.split()
        content = f'{header} {len(data)} {raw_data} 0 0'

        for sender, recipient in zip(
                self.clients,
                (*self.clients[1:], self.clients[0]),
        ):
            self.assertIsNone(recipient.receive())
            self.assertIsNone(sender.send(recipient.name, header, *data))
            self.assertEqual(
                recipient.receive(),
                f'{sender.name} {recipient.name} {content}',
            )
            self.assertIsNone(recipient.receive())

        for sender, recipient in zip(
                (*self.clients[1:], self.clients[0]),
                self.clients,
        ):
            self.assertIsNone(recipient.receive())
            self.assertIsNone(sender.send(recipient.name, header, *data))
            self.assertEqual(
                recipient.receive(),
                f'{sender.name} {recipient.name} {content}',
            )
            self.assertIsNone(recipient.receive())

    def test_bidirectional_communication(self):
        client_a = self.clients[0]
        client_b = self.clients[1]
        header = 'USA'
        raw_data = 'United States of America'
        data = raw_data.split()
        content = f'{header} {len(data)} {raw_data} 0 0'
        count = 10
        sub_count = 5

        for _ in range(count):
            self.assertIsNone(client_a.receive())
            self.assertIsNone(client_b.receive())

            for _ in range(sub_count):
                self.assertIsNone(client_a.send(client_b.name, header, *data))

            for _ in range(sub_count):
                self.assertEqual(
                    client_b.receive(),
                    f'{client_a.name} {client_b.name} {content}',
                )

            self.assertIsNone(client_a.receive())
            self.assertIsNone(client_b.receive())

            for _ in range(sub_count):
                self.assertIsNone(client_b.send(client_a.name, header, *data))

            for _ in range(sub_count):
                self.assertEqual(
                    client_a.receive(),
                    f'{client_b.name} {client_a.name} {content}',
                )

            self.assertIsNone(client_a.receive())
            self.assertIsNone(client_b.receive())

    def test_loopback_communication(self):
        client = self.clients[0]
        header = 'numbers'
        raw_data = '0 1 2 3 4 5 6 7 8 9'
        data = raw_data.split()
        content = f'{header} {len(data)} {raw_data} 0 0'
        count = 10

        for _ in range(count):
            self.assertIsNone(client.receive())
            self.assertEqual(
                client.send(client.name, header, *data),
                f'{client.name} {client.name} {content}',
            )
            self.assertIsNone(client.receive())


if __name__ == '__main__':
    main()
