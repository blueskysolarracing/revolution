from time import sleep

while True:
    with environment.contexts() as ctx:
        print(
            f"HV voltage={ctx.power_battery_HV_bus_voltage:.5f} "
            f"HV current={ctx.power_battery_HV_current:.5f} | "
            f"LV voltage={ctx.power_battery_LV_bus_voltage:.5f} "
            f"LV current={ctx.power_battery_LV_current:.5f} | "
            f"supp voltage={ctx.power_battery_supp_voltage:.5f}"
        )
    sleep(0.5)