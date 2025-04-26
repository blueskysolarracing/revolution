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
        previous_array_relay_status_input = False
        previous_battery_relay_status_input = False

        while (
                not self._stoppage.wait(
                    self.environment.settings.power_monitor_timeout,
                )
        ):
            with self.environment.contexts() as contexts:
                array_relay_status_input = (
                    contexts.power_array_relay_status_input
                )
                battery_relay_status_input = (
                    contexts.power_battery_relay_status_input
                )

            # TODO: fetch/check for over/under-voltage/temperature/current
            # TODO: calculate SOC

            if (
                    not previous_array_relay_status_input
                    and array_relay_status_input
            ):
                pass  # TODO: close array relay

            if (
                    not previous_battery_relay_status_input
                    and battery_relay_status_input
            ):
                pass  # TODO: close battery relay

                with self.environment.contexts() as contexts:
                    contexts.motor_status_input = True

            if (
                    previous_array_relay_status_input
                    and not array_relay_status_input
            ):
                pass  # TODO: open array relay

            if (
                    previous_battery_relay_status_input
                    and not battery_relay_status_input
            ):
                with self.environment.contexts() as contexts:
                    contexts.motor_status_input = False

                pass  # TODO: open battery relay

            previous_array_relay_status_input = array_relay_status_input
            previous_battery_relay_status_input = battery_relay_status_input
