from dataclasses import dataclass
from logging import getLogger
from time import sleep
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
        previous_motor_status_input = False

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
                (
                    self
                    .environment
                    .peripheries
                    .power_array_relay_low_side_gpio
                    .write(True)
                )
                (
                    self
                    .environment
                    .peripheries
                    .power_array_relay_pre_charge_gpio
                    .write(True)
                )
                sleep(self.environment.settings.power_array_relay_timeout)
                (
                    self
                    .environment
                    .peripheries
                    .power_array_relay_high_side_gpio
                    .write(True)
                )
                (
                    self
                    .environment
                    .peripheries
                    .power_array_relay_pre_charge_gpio
                    .write(False)
                )

            if (
                    not previous_battery_relay_status_input
                    and battery_relay_status_input
            ):
                pass  # TODO: close battery relay

            if (
                    previous_array_relay_status_input
                    and not array_relay_status_input
            ):
                (
                    self
                    .environment
                    .peripheries
                    .power_array_relay_low_side_gpio
                    .write(False)
                )
                (
                    self
                    .environment
                    .peripheries
                    .power_array_relay_high_side_gpio
                    .write(False)
                )
                (
                    self
                    .environment
                    .peripheries
                    .power_array_relay_pre_charge_gpio
                    .write(False)
                )

            if (
                    previous_battery_relay_status_input
                    and not battery_relay_status_input
            ):
                with self.environment.contexts() as contexts:
                    contexts.motor_status_input = False

                pass  # TODO: open battery relay

            motor_status_input = (
                array_relay_status_input
                and battery_relay_status_input
            )

            if previous_motor_status_input != motor_status_input:
                with self.environment.contexts() as contexts:
                    contexts.motor_status_input = motor_status_input

            previous_array_relay_status_input = array_relay_status_input
            previous_battery_relay_status_input = battery_relay_status_input
            previous_motor_status_input = motor_status_input
