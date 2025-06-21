from time import sleep

while True:
    # input_ = float(input())

    # with environment.contexts() as ctx:
    #     print(ctx.motor_status_input)
    #     print(ctx.motor_acceleration_input)
    #     print(ctx.power_battery_heartbeat_timestamp)
    #     print(ctx.motor_heartbeat_timestamp)
    #     # print(ctx.power_battery_cell_voltages)
    #     # print(ctx.power_battery_thermistor_temperatures)
    #     # print(ctx.power_battery_relay_status_input)
    #     # print(ctx.power_battery_relay_status)
    #     ctx.motor_acceleration_input = input_

    sleep(0.5)

    with environment.contexts() as ctx:
        print(f"motor_acceleration_input {ctx.motor_acceleration_input:.5f}")
        print(f"battery {ctx.power_psm_battery_current:.5f}A {ctx.power_psm_battery_voltage:.5f}V")
        print(f"array   {ctx.power_psm_array_current:.5f}A {ctx.power_psm_array_voltage:.5f}V")
        print(f"motor   {ctx.power_psm_motor_current:.5f}A {ctx.power_psm_motor_voltage:.5f}V")
        print(f"motor_varable_field_magnet_position={ctx.motor_variable_field_magnet_position}")

        print(f"voltage flags: {any(ctx.power_battery_cell_flags)}\nthermistor flags: {any(ctx.power_battery_thermistor_flags)}")
        # print(ctx.power_battery_cell_voltages)
        # print(ctx.power_battery_thermistor_temperatures)
        # print(ctx.power_battery_relay_status_input)
        # print(ctx.power_battery_relay_status)
        # print(ctx.power_battery_discharge_status)

        # print(ctx.motor_status_input)
        # print(ctx.motor_acceleration_input)
        # print(ctx.power_battery_heartbeat_timestamp)
        # print(ctx.motor_heartbeat_timestamp)
        # print(ctx.power_battery_cell_voltages)
        # print(ctx.power_battery_thermistor_temperatures)
        # print(ctx.power_battery_relay_status_input)
        # print(ctx.power_battery_relay_status)

        print()
