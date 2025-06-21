from time import sleep

for i in range(10000):
    with environment.contexts() as ctx:
        print(ctx.power_battery_electric_safe_discharge_status)
    sleep(0.1)

environment.stop()
