from dataclasses import dataclass
from hashlib import md5
from logging import getLogger
from statistics import mean
from typing import ClassVar

from databrief import dump

from revolution.application import Application
from revolution.environment import Endpoint, Header, Message
from revolution.worker import Worker

_logger = getLogger(__name__)


@dataclass
class Telemetry(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.TELEMETRY

    @dataclass
    class Data:
        velocity: float
        array_current: float
        array_voltage: float
        motor_current: float
        motor_voltage: float
        battery_state_of_charge: float
        latitude: float
        longitude: float

        def serialize(self) -> bytes:
            return dump(self)

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
                velocity = contexts.motor_velocity
                array_current = contexts.power_psm_array_current
                array_voltage = contexts.power_psm_array_voltage
                motor_current = contexts.power_psm_motor_current
                motor_voltage = contexts.power_psm_motor_voltage
                state_of_charges = (
                    contexts.power_battery_state_of_charges.copy()
                )
                latitude = contexts.miscellaneous_latitude
                longitude = contexts.miscellaneous_longitude

            data = self.Data(
                velocity,
                array_current,
                array_voltage,
                motor_current,
                motor_voltage,
                mean(state_of_charges),
                latitude,
                longitude,
            )
            data_token = data.serialize()
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
            can_message = self.environment.peripheries.general_can_bus.recv(
                self.environment.settings.telemetry_timeout,
            )

            if can_message is not None:
                message = Message(Header.CAN, (can_message,))

                self.environment.send_all(message)
