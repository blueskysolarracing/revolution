from dataclasses import dataclass
from hashlib import md5
from logging import getLogger
from typing import ClassVar

from revolution.application import Application
from revolution.environment import Endpoint, Header, Message
from revolution.worker import Worker

_logger = getLogger(__name__)


@dataclass
class Telemetry(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.TELEMETRY

    def _setup(self) -> None:
        super()._setup()

        self._telemetry_worker = Worker(target=self._telemetry)
        self._can_worker = Worker(target=self._can)

        self._telemetry_worker.start()
        self._can_worker.start()

    def _teardown(self) -> None:
        self._telemetry_worker.join()
        self._can_worker.join()

    def _telemetry(self) -> None:
        while (
                not self._stoppage.wait(
                    self.environment.settings.telemetry_timeout,
                )
        ):
            with self.environment.contexts() as contexts:
                assert hasattr(contexts, '_resource')

                data_token = contexts._resource.serialize()

            checksum_token = md5(data_token).hexdigest()
            tokens = (
                self.environment.settings.telemetry_begin_token,
                data_token.hex().encode(),
                self.environment.settings.telemetry_separator_token,
                checksum_token.encode(),
                self.environment.settings.telemetry_end_token,
            )
            raw_data = b''.join(tokens)

            self.environment.peripheries.telemetry_radio_serial.write(raw_data)
            self.environment.peripheries.telemetry_radio_serial.flush()

    def _can(self) -> None:
        while not self._stoppage.is_set():
            can_message = self.environment.peripheries.can_bus.recv(
                self.environment.settings.telemetry_timeout,
            )

            if can_message is not None:
                message = Message(Header.CAN, (can_message,))

                self.environment.send_all(message)
