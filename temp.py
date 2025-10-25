from time import sleep

while True:
    with environment.contexts() as ctx:
        # print(
        #     f"L:{ctx.miscellaneous_left_wheel_accelerations} | "
        #     f"R:{ctx.miscellaneous_right_wheel_accelerations}"
        # )

        print(f'horn={ctx.miscellaneous_horn_status_input}'
              f'reverse={ctx.motor_direction_input}'
              f'regen={ctx.motor_regeneration_status_input}'
              f'array={ctx.power_array_relay_status_input}'
              f'batt={ctx.power_battery_relay_status_input}'
              f'left={ctx.miscellaneous_left_indicator_light_status_input}'
              f'right={ctx.miscellaneous_right_indicator_light_status_input}'
              f'drl={ctx.miscellaneous_daytime_running_lights_status_input}'
              f'cc={ctx.motor_cruise_control_status_input}'
              f'vfm_up={ctx.motor_variable_field_magnet_up_input}'
              f'vfm_down={ctx.motor_variable_field_magnet_down_input}'
        )
    sleep(0.5)
