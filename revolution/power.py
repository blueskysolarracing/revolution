from dataclasses import dataclass
from logging import getLogger
from time import sleep, time
from typing import ClassVar

from battlib import EKFSOCEstimator
from can import Message

from revolution.application import Application
from revolution.battery_management_system import (
    BATTERY_CELL_COUNT,
    BusVoltageAndCurrentInformation,
    CellVoltagesInformation,
    OvervoltageTemperatureAndCurrentFlagsInformation,
    StatusesInformation,
    ThermistorTemperaturesInformation,
    UndervoltageAndTemperatureFlagsInformation,
)
from revolution.environment import Endpoint
from revolution.worker import Worker

_logger = getLogger(__name__)


@dataclass
class Power(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.POWER

    def _setup(self) -> None:
        super()._setup()

        self._monitor_worker = Worker(target=self._monitor)
        self._soc_worker = Worker(target=self._soc)

        self._monitor_worker.start()
        self._soc_worker.start()

    def _teardown(self) -> None:
        self._monitor_worker.join()
        self._soc_worker.join()

    def _monitor(self) -> None:
        previous_array_relay_status_input = False
        previous_battery_relay_status_input = False
        previous_all_relay_status_input = False
        previous_discharge_status = False

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
                battery_relay_status = contexts.power_battery_relay_status
                battery_electric_safe_discharge_status = (
                    contexts.power_battery_electric_safe_discharge_status
                )
                battery_discharge_status = (
                    contexts.power_battery_discharge_status
                )
                battery_cell_flags = contexts.power_battery_cell_flags.copy()
                battery_thermistor_flags = (
                    contexts.power_battery_thermistor_flags.copy()
                )
                battery_current_flag = contexts.power_battery_current_flag

            if (
                    battery_electric_safe_discharge_status
                    or battery_discharge_status
                    or any(battery_cell_flags)
                    or any(battery_thermistor_flags)
                    or battery_current_flag
            ):
                array_relay_status_input = False
                battery_relay_status_input = False
                discharge_status = True
            else:
                discharge_status = False

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
            elif (
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
                    not previous_battery_relay_status_input
                    and battery_relay_status_input
            ):
                (
                    self
                    .environment
                    .peripheries
                    .power_battery_management_system
                    .close_relay()
                )
            elif (
                    previous_battery_relay_status_input
                    and not battery_relay_status_input
            ):
                (
                    self
                    .environment
                    .peripheries
                    .power_battery_management_system
                    .open_relay()
                )

            all_relay_status_input = (
                array_relay_status_input
                and battery_relay_status
            )

            if previous_all_relay_status_input != all_relay_status_input:
                (
                    self
                    .environment
                    .peripheries
                    .power_point_tracking_switch_gpio
                    .write(all_relay_status_input)
                )

                with self.environment.contexts() as contexts:
                    contexts.motor_status_input = all_relay_status_input

            if (
                    not battery_relay_status
                    and not previous_discharge_status
                    and discharge_status
            ):
                assert (
                    not array_relay_status_input
                    and not battery_relay_status_input
                )

                (
                    self
                    .environment
                    .peripheries
                    .power_battery_management_system
                    .discharge()
                )

            previous_array_relay_status_input = array_relay_status_input
            previous_battery_relay_status_input = battery_relay_status_input
            previous_all_relay_status_input = all_relay_status_input
            previous_discharge_status = discharge_status

    def _soc(self) -> None:
        estimators: list[EKFSOCEstimator | None] = [
            None for _ in range(BATTERY_CELL_COUNT)
        ]
        previous_time = time()

        while (
                not self._stoppage.wait(
                    self.environment.settings.power_soc_timeout,
                )
        ):
            with self.environment.contexts() as contexts:
                battery_cell_voltages = (
                    contexts.power_battery_cell_voltages.copy()
                )
                battery_current = contexts.power_battery_current

                for i, estimator in enumerate(estimators):
                    if estimator is not None:
                        contexts.power_battery_state_of_charges[i] = (
                            estimator.soc
                        )

            time_ = time()
            time_difference = time_ - previous_time

            for i, (estimator, voltage) in enumerate(
                    zip(estimators, battery_cell_voltages),
            ):
                if estimator is None and voltage:
                    estimators[i] = EKFSOCEstimator(
                        self.environment.settings.power_battery,
                        voltage,
                    )
                elif estimator is not None:
                    estimator.step(
                        dt=time_difference,
                        i_in=battery_current,
                        measured_v=voltage,
                    )

            previous_time = time_

    def _handle_can(self, message: Message) -> None:
        super()._handle_can(message)

        information = (
            self
            .environment
            .peripheries
            .power_battery_management_system
            .parse(message)
        )

        if information is None:
            return

        with self.environment.contexts() as contexts:
            if isinstance(information, CellVoltagesInformation):
                for i, voltage in information.data.items():
                    contexts.power_battery_cell_voltages[i] = voltage
            elif isinstance(information, ThermistorTemperaturesInformation):
                for i, temperature in information.data.items():
                    contexts.power_battery_thermistor_temperatures[i] = (
                        temperature
                    )
            elif isinstance(information, BusVoltageAndCurrentInformation):
                contexts.power_battery_bus_voltage = information.bus_voltage
                contexts.power_battery_current = information.current
            elif isinstance(information, StatusesInformation):
                contexts.power_battery_relay_status = information.relay_status
                contexts.power_battery_electric_safe_discharge_status = (
                    information.electric_safe_discharge_status
                )
                contexts.power_battery_discharge_status = (
                    information.discharge_status
                )
            elif (
                    isinstance(
                        information,
                        (
                            OvervoltageTemperatureAndCurrentFlagsInformation
                            | UndervoltageAndTemperatureFlagsInformation
                        ),
                    )
            ):
                for i, flag in information.cell_flags.items():
                    contexts.power_battery_cell_flags[i] -= (
                        contexts.power_battery_cell_flags[i]
                        & information.CELL_FLAG
                    )
                    contexts.power_battery_cell_flags[i] |= flag

                for i, flag in information.thermistor_flags.items():
                    contexts.power_battery_thermistor_flags[i] -= (
                        contexts.power_battery_thermistor_flags[i]
                        & information.THERMISTOR_FLAG
                    )
                    contexts.power_battery_thermistor_flags[i] |= flag

                contexts.power_battery_current_flag -= (
                    contexts.power_battery_current_flag
                    & information.CURRENT_FLAG
                )
                contexts.power_battery_current_flag |= (
                    information.current_flag
                )
