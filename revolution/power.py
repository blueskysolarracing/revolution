from dataclasses import dataclass
from logging import getLogger
from time import sleep, time
from typing import ClassVar

from battlib import EKFSOCEstimator
from can import Message

from revolution.application import Application
from revolution.battery_management_system import (
    BATTERY_CELL_COUNT,
    BATTERY_THERMISTOR_COUNT,
    CellVoltagesInformation,
    LVInformation,
    OverBatteryFlagsHoldInformation,
    OverBatteryFlagsInformation,
    OvercurrentHoldInformation,
    OvertemperatureHoldInformation,
    OvervoltageHoldInformation,
    StatusesAndHVInformation,
    ThermistorTemperaturesInformation,
    UnderBatteryFlagsHoldInformation,
    UnderBatteryFlagsInformation,
    UndercurrentHoldInformation,
    UndertemperatureHoldInformation,
    UndervoltageHoldInformation,
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
        def array_relay(status: bool) -> None:
            (
                self
                .environment
                .peripheries
                .power_array_relay_low_side_gpio
                .write(status)
            )
            (
                self
                .environment
                .peripheries
                .power_array_relay_high_side_gpio
                .write(status)
            )
            if status:
                sleep(self.environment.settings.power_array_relay_timeout)
            (
                self
                .environment
                .peripheries
                .power_array_relay_pre_charge_gpio
                .write(status)
            )

        def ppt_relay(status: bool) -> None:
            if status:
                sleep(self.environment.settings.power_point_tracking_timeout)
            (
                self
                .environment
                .peripheries
                .power_point_tracking_switch_1_gpio
                .write(status)
            )
            (
                self
                .environment
                .peripheries
                .power_point_tracking_switch_2_gpio
                .write(status)
            )
            if not status:
                sleep(self.environment.settings.power_point_tracking_timeout)

        previous_array_relay_status_input = False

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
                battery_heartbeat_timestamp = (
                    contexts.power_battery_heartbeat_timestamp
                )
                battery_mean_state_of_charge = (
                    contexts.power_battery_mean_state_of_charge
                )

            battery_heartbeat_working = (
                (time() - battery_heartbeat_timestamp)
                < self.environment.settings.power_battery_can_timeout
            )
            with self.environment.contexts() as contexts:
                contexts.power_battery_heartbeat_working = (
                    battery_heartbeat_working
                )

            if (
                battery_mean_state_of_charge >= (
                    self
                    .environment
                    .settings
                    .power_disable_charging_battery_soc_threshold
                ) or not battery_relay_status
            ):
                array_relay_status_input = False

            if (
                    not previous_array_relay_status_input
                    and array_relay_status_input
            ):
                array_relay(True)
                ppt_relay(True)
                with self.environment.contexts() as contexts:
                    contexts.power_array_relay_status = True
            elif (
                    previous_array_relay_status_input
                    and not array_relay_status_input
            ):
                ppt_relay(False)
                array_relay(False)
                with self.environment.contexts() as contexts:
                    contexts.power_array_relay_status = False

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

            previous_array_relay_status_input = array_relay_status_input

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

            self.environment.peripheries.driver_steering_wheel.set_fault_light(
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
            # Important
            if isinstance(information, StatusesAndHVInformation):
                contexts.power_battery_relay_status = information.relay_status
                contexts.power_battery_electric_safe_discharge_status = (
                    information.electric_safe_discharge_status
                )
                contexts.power_battery_discharge_status = (
                    information.discharge_status
                )
                contexts.power_battery_flags_hold = BatteryFlag(
                    information.flag_hold
                )
                contexts.power_battery_HV_voltage = information.HV_voltage
                contexts.power_battery_HV_current = information.HV_current
            elif (
                    isinstance(
                        information,
                        (
                            OverBatteryFlagsInformation
                            | UnderBatteryFlagsInformation
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
            elif isinstance(information, LVInformation):
                contexts.power_battery_LV_voltage = information.LV_voltage
                contexts.power_battery_LV_current = information.LV_current
                contexts.power_battery_supp_voltage = information.supp_voltage
                contexts.power_battery_rolling_min_LV_voltage = (
                    information.rolling_min_LV_voltage
                )

            # Battery Flag Event
            elif (
                    isinstance(
                        information,
                        (
                            OverBatteryFlagsHoldInformation
                            | UnderBatteryFlagsHoldInformation
                        ),
                    )
            ):
                for i, flag in information.cell_flags.items():
                    contexts.power_battery_hold_cell_flags[i] -= (
                        contexts.power_battery_hold_cell_flags[i]
                        & information.CELL_FLAG
                    )
                    contexts.power_battery_hold_cell_flags[i] |= flag

                for i, flag in information.thermistor_flags.items():
                    contexts.power_battery_hold_thermistor_flags[i] -= (
                        contexts.power_battery_hold_thermistor_flags[i]
                        & information.THERMISTOR_FLAG
                    )
                    contexts.power_battery_hold_thermistor_flags[i] |= flag

                contexts.power_battery_hold_current_flag -= (
                    contexts.power_battery_hold_current_flag
                    & information.CURRENT_FLAG
                )
                contexts.power_battery_hold_current_flag |= (
                    information.current_flag
                )
            elif isinstance(information, OvervoltageHoldInformation):
                contexts.power_battery_hold_elapsed_count = max(
                    information.hold_elapsed_count,
                    contexts.power_battery_hold_elapsed_count
                )
                contexts.power_battery_hold_OV_count = (
                    information.hold_OV_count
                )
                contexts.power_battery_hold_OV_max = (
                    information.hold_OV_max
                )
            elif isinstance(information, UndervoltageHoldInformation):
                contexts.power_battery_hold_elapsed_count = max(
                    information.hold_elapsed_count,
                    contexts.power_battery_hold_elapsed_count
                )
                contexts.power_battery_hold_UV_count = (
                    information.hold_UV_count
                )
                contexts.power_battery_hold_UV_min = (
                    information.hold_UV_min
                )
            elif isinstance(information, OvertemperatureHoldInformation):
                contexts.power_battery_hold_elapsed_count = max(
                    information.hold_elapsed_count,
                    contexts.power_battery_hold_elapsed_count
                )
                contexts.power_battery_hold_OT_count = (
                    information.hold_OT_count
                )
                contexts.power_battery_hold_OT_max = (
                    information.hold_OT_max
                )
            elif isinstance(information, UndertemperatureHoldInformation):
                contexts.power_battery_hold_elapsed_count = max(
                    information.hold_elapsed_count,
                    contexts.power_battery_hold_elapsed_count
                )
                contexts.power_battery_hold_UT_count = (
                    information.hold_UT_count
                )
                contexts.power_battery_hold_UT_min = (
                    information.hold_UT_min
                )
            elif isinstance(information, OvercurrentHoldInformation):
                contexts.power_battery_hold_elapsed_count = max(
                    information.hold_elapsed_count,
                    contexts.power_battery_hold_elapsed_count
                )
                contexts.power_battery_hold_OC_count = (
                    information.hold_OC_count
                )
                contexts.power_battery_hold_OC_max = (
                    information.hold_OC_max
                )
            elif isinstance(information, UndercurrentHoldInformation):
                contexts.power_battery_hold_elapsed_count = max(
                    information.hold_elapsed_count,
                    contexts.power_battery_hold_elapsed_count
                )
                contexts.power_battery_hold_UC_count = (
                    information.hold_UC_count
                )
                contexts.power_battery_hold_UC_min = (
                    information.hold_UC_min
                )

            # Voltages / Temperatures
            elif isinstance(information, CellVoltagesInformation):
                for i, voltage in information.data.items():
                    if i < BATTERY_CELL_COUNT:
                        contexts.power_battery_cell_voltages[i] = voltage
            elif isinstance(information, ThermistorTemperaturesInformation):
                for i, temperature in information.data.items():
                    if i < BATTERY_THERMISTOR_COUNT:
                        contexts.power_battery_thermistor_temperatures[i] = (
                            temperature
                        )

            contexts.power_battery_heartbeat_timestamp = time()
