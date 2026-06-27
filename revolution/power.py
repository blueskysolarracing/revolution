from dataclasses import dataclass, fields
from datetime import datetime
from logging import getLogger
from os import makedirs
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
    UndervoltageTemperatureAndCurrentFlagsInformation,
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
        self._power_log_worker = Worker(target=self._power_log)

        self._monitor_worker.start()
        self._soc_worker.start()
        self._psm_worker.start()
        self._steering_wheel_led_worker.start()
        self._power_log_worker.start()

    def _teardown(self) -> None:
        self._monitor_worker.join()
        self._soc_worker.join()
        self._psm_worker.join()
        self._steering_wheel_led_worker.join()
        self._power_log_worker.join()

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
                battery_flags = contexts.power_battery_flags
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
                    or not battery_heartbeat_working
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
                battery_clear_input = True
            else:
                battery_clear_input = False

            all_relay_status = (
                array_relay_status_input
                and battery_relay_status_input
                and battery_relay_status
            )

            if battery_electric_safe_discharge_status:
                battery_electric_safe_discharge_flag = True

            if previous_all_relay_status and not all_relay_status:
                ppt_relay(False)

            if (
                    not previous_array_relay_status_input
                    and array_relay_status_input
            ):
                array_relay(True)
                with self.environment.contexts() as contexts:
                    contexts.power_array_relay_status = True
            elif (
                    previous_array_relay_status_input
                    and not array_relay_status_input
            ):
                array_relay(False)
                with self.environment.contexts() as contexts:
                    contexts.power_array_relay_status = False

            if not previous_all_relay_status and all_relay_status:
                ppt_relay(True)

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

            if (
                    not battery_relay_status
                    and not battery_discharge_status
                    and battery_discharge_status_input
            ):
                (
                    self
                    .environment
                    .peripheries
                    .power_battery_management_system
                    .discharge()
                )

            if battery_discharge_status and battery_clear_input:
                (
                    self
                    .environment
                    .peripheries
                    .power_battery_management_system
                    .clear()
                )
                battery_electric_safe_discharge_flag = False

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

            self.environment.peripheries.driver_steering_wheel.set_fault_light(
                status,
            )

    def _power_log(self) -> None:
        filepath = (
            self.environment.settings.general_log_filepath
        )

        print_log = filepath != ''

        if not print_log:
            return

        @dataclass
        class PowerLogData:
            miscellaneous_brake_status_input: bool

            motor_status_input: bool
            motor_acceleration_input: float
            motor_cruise_control_velocity: float
            motor_regeneration_status_input: bool
            motor_variable_field_magnet_up_input: int
            motor_variable_field_magnet_down_input: int
            motor_variable_field_magnet_position: int
            motor_velocity: float
            motor_heartbeat_timestamp: float
            motor_heartbeat_working: bool

            motor_controller_sent_current: float
            motor_controller_sent_velocity: float
            motor_controller_limit_flags: int
            motor_controller_error_flags: int
            motor_controller_active_motor: int
            motor_controller_transmit_error_count: int
            motor_controller_receive_error_count: int
            motor_controller_bus_voltage: float
            motor_controller_bus_current: float
            motor_controller_vehicle_velocity: float
            motor_controller_phase_B_current: float
            motor_controller_phase_C_current: float
            motor_controller_Vq: float
            motor_controller_Vd: float
            motor_controller_Iq: float
            motor_controller_Id: float
            motor_controller_BEMFq: float
            motor_controller_BEMFd: float
            motor_controller_supply_15v: float
            motor_controller_supply_1_9v: float
            motor_controller_supply_3_3v: float
            motor_controller_motor_temp: float
            motor_controller_heat_sink_temp: float
            motor_controller_dsp_board_temp: float
            motor_controller_odometer: float
            motor_controller_dc_bus_amphours: float
            motor_controller_slip_speed: float

            power_array_relay_status_input: bool
            power_array_relay_status: bool
            power_battery_relay_status_input: bool

            power_battery_min_cell_voltage: float
            power_battery_max_cell_voltage: float
            power_battery_mean_cell_voltage: float
            power_battery_min_thermistor_temperature: float
            power_battery_max_thermistor_temperature: float
            power_battery_mean_thermistor_temperature: float

            power_battery_HV_bus_voltage: float
            power_battery_HV_current: float
            power_battery_LV_bus_voltage: float
            power_battery_LV_current: float
            power_battery_supp_voltage: float

            power_battery_relay_status: bool
            power_battery_electric_safe_discharge_status: bool
            power_battery_discharge_status: bool
            power_battery_flags: BatteryFlag
            power_battery_flags_hold: BatteryFlag
            power_battery_heartbeat_timestamp: float
            power_battery_heartbeat_working: bool

            power_battery_min_state_of_charge: float
            power_battery_max_state_of_charge: float
            power_battery_mean_state_of_charge: float

            power_psm_battery_current: float
            power_psm_battery_voltage: float
            power_psm_array_current: float
            power_psm_array_voltage: float
            power_psm_motor_current: float
            power_psm_motor_voltage: float

        makedirs(filepath, exist_ok=True)
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = open(f'{filepath}{now}_power_log.csv', 'w')

        print('time, ', end='', file=log_file)
        for field in fields(PowerLogData):
            print(f'{field.name}, ', end='', file=log_file)
        print(file=log_file)
        log_file.flush()

        while (
                not self._stoppage.wait(
                    (
                        self
                        .environment
                        .settings
                        .power_log_timeout
                    ),
                )
        ):
            print(f'{datetime.now().time()}, ', end='', file=log_file)
            with self.environment.contexts() as contexts:
                for field in fields(PowerLogData):
                    print(
                        f'{getattr(contexts, field.name)}, ',
                        end='',
                        file=log_file
                    )
            print(file=log_file)
            log_file.flush()

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
                contexts.power_battery_flags_hold = information.flag_hold
                contexts.power_battery_supp_voltage = information.supp_voltage
            elif (
                    isinstance(
                        information,
                        (
                            OvervoltageTemperatureAndCurrentFlagsInformation
                            | UndervoltageTemperatureAndCurrentFlagsInformation
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
