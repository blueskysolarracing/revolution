from dataclasses import dataclass
from datetime import datetime
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

            self.environment.peripheries.driver_steering_wheel.set_fault_light(
                status,
            )

    def _power_log(self) -> None:
        filepath = (
            self.environment.settings.general_log_filepath
        )
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = open(f'{filepath}{now}_power_log.csv', "w")
        print(
            'time, '
            'acceleration_input, '
            'cruise_control, '
            'regen, '
            'vfm, '
            'motor_velocity, '
            'motor_controller_sent_value_current, '
            'motor_controller_sent_value_velocity, '
            'motor_controller_limit_flags, '
            'motor_controller_error_flags, '
            'motor_controller_active_motor, '
            'motor_controller_transmit_error_count, '
            'motor_controller_receive_error_count, '
            'motor_controller_bus_voltage, '
            'motor_controller_bus_current, '
            'motor_controller_vehicle_velocity, '
            'motor_controller_phase_B_current, '
            'motor_controller_phase_C_current, '
            'motor_controller_Vq, '
            'motor_controller_Vd, '
            'motor_controller_Iq, '
            'motor_controller_Id, '
            'motor_controller_BEMFq, '
            'motor_controller_BEMFd, '
            'motor_controller_supply_15v, '
            'motor_controller_supply_1_9v, '
            'motor_controller_supply_3_3v, '
            'motor_controller_motor_temp, '
            'motor_controller_heat_sink_temp, '
            'motor_controller_dsp_board_temp, '
            'motor_controller_odometer, '
            'motor_controller_dc_bus_amphours, '
            'motor_controller_slip_speed, '
            'psm_battery_current, '
            'psm_battery_voltage, '
            'psm_array_current, '
            'psm_array_voltage, '
            'psm_motor_current, '
            'psm_motor_voltage, '
            'bfm_HV_current, ',
            file=log_file,
        )
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
            with self.environment.contexts() as contexts:
                acceleration_input = contexts.motor_acceleration_input
                cruise_control = contexts.motor_cruise_control_status_input
                regen = contexts.motor_regeneration_status_input
                vfm = contexts.motor_variable_field_magnet_position
                motor_velocity = contexts.motor_velocity
                motor_controller_sent_values = (
                    contexts.motor_controller_sent_values
                )

                limit_flags = contexts.motor_controller_limit_flags
                error_flags = contexts.motor_controller_error_flags
                active_motor = contexts.motor_controller_active_motor
                transmit_error_count = (
                    contexts.motor_controller_transmit_error_count
                )
                receive_error_count = (
                    contexts.motor_controller_receive_error_count
                )
                mc_bus_voltage = contexts.motor_controller_bus_voltage
                mc_bus_current = contexts.motor_controller_bus_current
                vehicle_velocity = contexts.motor_controller_vehicle_velocity
                phase_B_current = contexts.motor_controller_phase_B_current
                phase_C_current = contexts.motor_controller_phase_C_current
                Vq = contexts.motor_controller_Vq
                Vd = contexts.motor_controller_Vd
                Iq = contexts.motor_controller_Iq
                Id = contexts.motor_controller_Id
                BEMFq = contexts.motor_controller_BEMFq
                BEMFd = contexts.motor_controller_BEMFd
                supply_15v = contexts.motor_controller_supply_15v
                supply_1_9v = contexts.motor_controller_supply_1_9v
                supply_3_3v = contexts.motor_controller_supply_3_3v
                motor_temp = contexts.motor_controller_motor_temp
                heat_sink_temp = contexts.motor_controller_heat_sink_temp
                dsp_board_temp = contexts.motor_controller_dsp_board_temp
                odometer = contexts.motor_controller_odometer
                dc_bus_amphours = contexts.motor_controller_dc_bus_amphours
                slip_speed = contexts.motor_controller_slip_speed

                psm_battery_current = contexts.power_psm_battery_current
                psm_battery_voltage = contexts.power_psm_battery_voltage
                psm_array_current = contexts.power_psm_array_current
                psm_array_voltage = contexts.power_psm_array_voltage
                psm_motor_current = contexts.power_psm_motor_current
                psm_motor_voltage = contexts.power_psm_motor_voltage

                bms_HV_current = contexts.power_battery_HV_current
            
            print(
                f'{datetime.now().time()}, '
                f'{acceleration_input}, '
                f'{cruise_control}, '
                f'{regen}, '
                f'{vfm}, '
                f'{motor_velocity}, '
                f'{motor_controller_sent_values[0]}, '
                f'{motor_controller_sent_values[1]}, '
                f'{limit_flags}, '
                f'{error_flags}, '
                f'{active_motor}, '
                f'{transmit_error_count}, '
                f'{receive_error_count}, '
                f'{mc_bus_voltage}, '
                f'{mc_bus_current}, '
                f'{vehicle_velocity}, '
                f'{phase_B_current}, '
                f'{phase_C_current}, '
                f'{Vq}, '
                f'{Vd}, '
                f'{Iq}, '
                f'{Id}, '
                f'{BEMFq}, '
                f'{BEMFd}, '
                f'{supply_15v}, '
                f'{supply_1_9v}, '
                f'{supply_3_3v}, '
                f'{motor_temp}, '
                f'{heat_sink_temp}, '
                f'{dsp_board_temp}, '
                f'{odometer}, '
                f'{dc_bus_amphours}, '
                f'{slip_speed}, '
                f'{psm_battery_current}, '
                f'{psm_battery_voltage}, '
                f'{psm_array_current}, '
                f'{psm_array_voltage}, '
                f'{psm_motor_current}, '
                f'{psm_motor_voltage}, '
                f'{bms_HV_current}, ',
                file=log_file
            )
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
