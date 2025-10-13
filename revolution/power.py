from dataclasses import dataclass
from logging import getLogger
from time import sleep, time
from typing import ClassVar

from battlib import EKFSOCEstimator
from can import Message

from revolution.application import Application
from revolution.battery_management_system import (
    BatteryFlag,
    BATTERY_CELL_COUNT,
    CellVoltagesInformation,
    HVBusVoltageAndCurrentInformation,
    LVBusVoltageAndCurrentInformation,
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
        self._psm_worker = Worker(target=self._psm)
        self._steering_wheel_led_worker = Worker(
            target=self._steering_wheel_led,
        )

        self._monitor_worker.start()
        self._soc_worker.start()
        self._psm_worker.start()
        self._steering_wheel_led_worker.start()

    def _teardown(self) -> None:
        self._monitor_worker.join()
        self._soc_worker.join()
        self._psm_worker.join()
        self._steering_wheel_led_worker.join()

    def _monitor(self) -> None:
        previous_array_relay_status_input = False
        previous_battery_relay_status = False
        previous_all_relay_status = False
        battery_electric_safe_discharge_flag = False

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
                battery_mean_state_of_charge = (
                    contexts.power_battery_mean_state_of_charge
                )
                psm_battery_current = contexts.power_psm_battery_current

            battery_current_flag_psm = 0
            if (
                    psm_battery_current
                    > self.environment.settings.power_battery_overcurrent_limit
            ):
                battery_current_flag_psm |= BatteryFlag.OVERCURRENT
            if (
                    psm_battery_current
                    < (
                            self
                            .environment
                            .settings
                            .power_battery_undercurrent_limit
                    )
            ):
                battery_current_flag_psm |= BatteryFlag.UNDERCURRENT
            with self.environment.contexts() as contexts:
                # contexts.power_battery_current_flag |= battery_current_flag_psm
                battery_current_flag = contexts.power_battery_current_flag
                battery_flags = contexts.power_battery_flags

            if battery_flags:
                with self.environment.contexts() as contexts:
                    contexts.power_battery_flags_hold |= battery_flags
            if battery_mean_state_of_charge >= (
                self
                .environment
                .settings
                .power_disable_charging_battery_soc_threshold
            ):
                array_relay_status_input = False
            if (
                    (
                        battery_relay_status_input
                        and battery_electric_safe_discharge_status
                    )
                    or battery_discharge_status
                    or battery_flags
            ):
                array_relay_status_input = False
                battery_relay_status_input = False
                battery_discharge_status_input = True
            else:
                battery_discharge_status_input = False

            if (
                    not battery_relay_status_input
                    and not battery_electric_safe_discharge_status
                    and not battery_flags
                    and battery_electric_safe_discharge_flag
            ):
                battery_clear_status_input = True
            else:
                battery_clear_status_input = False

            all_relay_status = (
                array_relay_status_input
                and battery_relay_status_input
                and battery_relay_status
            )

            if battery_electric_safe_discharge_status:
                battery_electric_safe_discharge_flag = True

            if previous_all_relay_status and not all_relay_status:
                (
                    self
                    .environment
                    .peripheries
                    .power_point_tracking_switch_1_gpio
                    .write(False)
                )
                (
                    self
                    .environment
                    .peripheries
                    .power_point_tracking_switch_2_gpio
                    .write(False)
                )
                sleep(self.environment.settings.power_point_tracking_timeout)

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
                    .power_array_relay_high_side_gpio
                    .write(True)
                )
                sleep(self.environment.settings.power_array_relay_timeout)
                (
                    self
                    .environment
                    .peripheries
                    .power_array_relay_pre_charge_gpio
                    .write(True)
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

            if not previous_all_relay_status and all_relay_status:
                sleep(self.environment.settings.power_point_tracking_timeout)
                (
                    self
                    .environment
                    .peripheries
                    .power_point_tracking_switch_1_gpio
                    .write(True)
                )
                (
                    self
                    .environment
                    .peripheries
                    .power_point_tracking_switch_2_gpio
                    .write(True)
                )

            if not battery_relay_status and battery_relay_status_input:
                (
                    self
                    .environment
                    .peripheries
                    .power_battery_management_system
                    .close_relay()
                )
            elif battery_relay_status and not battery_relay_status_input:
                (
                    self
                    .environment
                    .peripheries
                    .power_battery_management_system
                    .open_relay()
                )

            if previous_battery_relay_status != battery_relay_status:
                with self.environment.contexts() as contexts:
                    contexts.motor_status_input = battery_relay_status

            if (
                    not battery_relay_status
                    and not battery_discharge_status
                    and battery_discharge_status_input
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

            if battery_discharge_status and battery_clear_status_input:
                (
                    self
                    .environment
                    .peripheries
                    .power_battery_management_system
                    .clear()
                )
                battery_electric_safe_discharge_flag = False
                with self.environment.contexts() as contexts:
                    contexts.power_battery_flags_hold = 0

            previous_array_relay_status_input = array_relay_status_input
            previous_battery_relay_status = battery_relay_status
            previous_all_relay_status = all_relay_status

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
                battery_current = contexts.power_battery_HV_current

                for i, estimator in enumerate(estimators):
                    if estimator is not None:
                        contexts.power_battery_state_of_charges[i] = (
                            estimator.soc.item()  # type: ignore[attr-defined]
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
                        i_in=-battery_current,
                        measured_v=voltage,
                    )

            previous_time = time_

    def _psm(self) -> None:
        while (
                not self._stoppage.wait(
                    self.environment.settings.power_psm_timeout,
                )
        ):
            motor_current = (
                self.environment.peripheries.power_psm_motor_ina229.current
            )
            motor_voltage = (
                self.environment.peripheries.power_psm_motor_ina229.bus_voltage
                * (
                        self
                        .environment
                        .settings
                        .power_psm_motor_ina229_voltage_correction_factor
                )
            )
            battery_current = (
                self.environment.peripheries.power_psm_battery_ina229.current
            )
            battery_voltage = (
                (
                    self
                    .environment
                    .peripheries
                    .power_psm_battery_ina229
                    .bus_voltage
                )
                * (
                        self
                        .environment
                        .settings
                        .power_psm_battery_ina229_voltage_correction_factor
                )
            )
            array_current = (
                self.environment.peripheries.power_psm_array_ina229.current
            )
            array_voltage = (
                self.environment.peripheries.power_psm_array_ina229.bus_voltage
                * (
                    self
                    .environment
                    .settings
                    .power_psm_array_ina229_voltage_correction_factor
                )
            )

            with self.environment.contexts() as contexts:
                contexts.power_psm_motor_current = motor_current
                contexts.power_psm_motor_voltage = motor_voltage
                contexts.power_psm_battery_current = battery_current
                contexts.power_psm_battery_voltage = battery_voltage
                contexts.power_psm_array_current = array_current
                contexts.power_psm_array_voltage = array_voltage

    def _steering_wheel_led(self) -> None:
        status = False

        while (
                not self._stoppage.wait(
                    self.environment.settings.power_steering_wheel_led_timeout,
                )
        ):
            with self.environment.contexts() as contexts:
                battery_discharge_status = (
                    contexts.power_battery_discharge_status
                )

            if battery_discharge_status:
                status = not status
            else:
                status = False

            self.environment.peripheries.power_steering_wheel_led_gpio.write(
                status,
            )

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
            elif isinstance(information, HVBusVoltageAndCurrentInformation):
                contexts.power_battery_HV_bus_voltage = information.bus_voltage
                contexts.power_battery_HV_current = information.current
            elif isinstance(information, LVBusVoltageAndCurrentInformation):
                contexts.power_battery_LV_bus_voltage = information.bus_voltage
                contexts.power_battery_LV_current = information.current
            elif isinstance(information, StatusesInformation):
                contexts.power_battery_relay_status = information.relay_status
                contexts.power_battery_electric_safe_discharge_status = (
                    information.electric_safe_discharge_status
                )
                contexts.power_battery_discharge_status = (
                    information.discharge_status
                )
                contexts.power_battery_supp_voltage = information.supp_voltage
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

            contexts.power_battery_heartbeat_timestamp = time()
