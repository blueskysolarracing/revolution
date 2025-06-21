from dataclasses import dataclass, fields
from hashlib import md5
from logging import getLogger
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
        motor_acceleration_input: float
        motor_cruise_control_status_input: bool
        motor_cruise_control_velocity: float
        motor_variable_field_magnet_position: int
        motor_velocity: float

        power_array_relay_status_input: bool
        power_battery_relay_status_input: bool
        power_battery_min_cell_voltage: float
        power_battery_max_cell_voltage: float
        power_battery_mean_cell_voltage: float
        power_battery_max_thermistor_temperature: float
        power_battery_mean_thermistor_temperature: float

        power_battery_bus_voltage: float
        power_battery_current: float
        power_battery_relay_status: bool
        power_battery_electric_safe_discharge_status: bool
        power_battery_discharge_status: bool

        power_battery_flags: int

        power_battery_min_state_of_charge: float
        power_battery_max_state_of_charge: float
        power_battery_mean_state_of_charge: float

        power_psm_battery_current: float
        power_psm_battery_voltage: float
        power_psm_array_current: float
        power_psm_array_voltage: float
        power_psm_motor_current: float
        power_psm_motor_voltage: float

        miscellaneous_orientation: dict[str, float]
        miscellaneous_latitude: float
        miscellaneous_longitude: float

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
            kwargs = {}

            with self.environment.contexts() as contexts:
                for field in fields(self.Data):
                    name = field.name
                    kwargs[name] = getattr(contexts, name)
                kwargs["miscellaneous_latitude"] = 0.0
                kwargs["miscellaneous_longitude"] = 0.0
            print("Fields: ", kwargs)
        
            data = self.Data(**kwargs)
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
