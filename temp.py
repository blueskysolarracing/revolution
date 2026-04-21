from time import sleep

while True:
    with environment.contexts() as ctx:
        # Front wheel sensors
        # print(
        #     f'L:{ctx.miscellaneous_left_wheel_accelerations} '
        #     f'{ctx.miscellaneous_left_wheel_accelerometer_working} | '
        #     f'R:{ctx.miscellaneous_right_wheel_accelerations} '
        #     f'{ctx.miscellaneous_right_wheel_accelerometer_working}'
        # )
        # print(
        #     f'imu orientation={ctx.miscellaneous_orientation} '
        #     f'{ctx.miscellaneous_orientation_imu_working}'
        # )

        # GPS
        # print(
        #     f'GPS latitude={ctx.miscellaneous_latitude} '
        #     f'longitude={ctx.miscellaneous_longitude} '
        #     f'altitude={ctx.miscellaneous_altitude} '
        #     f'fix_quality={ctx.miscellaneous_gps_fix_quality} '
        #     f'fix_quality_3d={ctx.miscellaneous_gps_fix_quality_3d} '
        #     f'satellites={ctx.miscellaneous_gps_satellites} '
        # )

        # Steering wheel
        print(
            f'horn={ctx.miscellaneous_horn_status_input} '
            f'reverse={ctx.motor_direction_input} '
            f'regen={ctx.motor_regeneration_status_input} '
            f'array={ctx.power_array_relay_status_input} '
            f'batt={ctx.power_battery_relay_status_input} '
            f'left={ctx.miscellaneous_left_indicator_light_status_input} '
            f'right={ctx.miscellaneous_right_indicator_light_status_input} '
            f'drl={ctx.miscellaneous_daytime_running_lights_status_input} '
            f'cc={ctx.motor_cruise_control_status_input} '
            f'vfm_up={ctx.motor_variable_field_magnet_up_input} '
            f'vfm_down={ctx.motor_variable_field_magnet_down_input}'
        )

        # VFM
        print(
            f'VFM={ctx.motor_variable_field_magnet_position} '
            f'motor_status={ctx.motor_status_input}'
        )

        # Power
        # print(
        #     f'motor_v={ctx.power_psm_motor_voltage:6.2f}  '
        #     f'motor_i={ctx.power_psm_motor_current:6.2f}  '
        #     f'battery_v={ctx.power_psm_battery_voltage:6.2f}  '
        #     f'battery_i={ctx.power_psm_battery_current:6.2f}  '
        #     f'bms_HV_i={ctx.power_battery_HV_current:6.2f}  '
        #     f'bms_LV_v={ctx.power_battery_LV_bus_voltage:6.2f}  '
        #     f'supp={ctx.power_battery_supp_voltage:6.2f}'
        # )


    sleep(0.5)
