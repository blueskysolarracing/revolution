from dataclasses import dataclass
from logging import getLogger
from typing import ClassVar

from revolution.application import Application
from revolution.environment import Endpoint
from revolution.worker import Worker

_logger = getLogger(__name__)


@dataclass
class Power(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.POWER

    def _setup(self) -> None:
        super()._setup()

        self._monitor_worker = Worker(target=self._monitor)

        self._monitor_worker.start()

    def _teardown(self) -> None:
        self._monitor_worker.join()

    def _monitor(self) -> None:
        previous_power_array_relay_status_input = False
        previous_power_battery_relay_status_input = False

        while (
                not self._stoppage.wait(
                    self.environment.settings.power_monitor_timeout,
                )
        ):
            with self.environment.contexts() as contexts:
                power_array_relay_status_input = (
                    contexts.power_array_relay_status_input
                )
                power_battery_relay_status_input = (
                    contexts.power_battery_relay_status_input
                )

            # TODO: fetch/check for over/under-voltage/temperature/current

            if (
                    not previous_power_array_relay_status_input
                    and power_array_relay_status_input
            ):
                self.environment.peripheries.power_pptmb_spi.transfer(
                    [],  # TODO: close array relay
                )

            if (
                    not previous_power_battery_relay_status_input
                    and power_battery_relay_status_input
            ):
                self.environment.peripheries.power_bms_spi.transfer(
                    [],  # TODO: close battery relay
                )

            if (
                    previous_power_array_relay_status_input
                    and not power_array_relay_status_input
            ):
                self.environment.peripheries.power_pptmb_spi.transfer(
                    [],  # TODO: open array relay
                )

            if (
                    previous_power_battery_relay_status_input
                    and not power_battery_relay_status_input
            ):
                self.environment.peripheries.power_bms_spi.transfer(
                    [],  # TODO: open battery relay
                )

            previous_power_array_relay_status_input = (
                power_array_relay_status_input
            )
            previous_power_battery_relay_status_input = (
                power_battery_relay_status_input
            )
