from time import sleep

sleep(10)

while True:
    with environment.contexts() as ctx:
        print(
            f'array input: {ctx.power_array_relay_status_input} '
            f'battery input: {ctx.power_battery_relay_status_input}\n'
            f'array status: {ctx.power_array_relay_status} '
            f'battery status: {ctx.power_battery_relay_status}\n'
        )

    user = input(
        'a: toggle array relay\nb: toggle battery relay\ntype a or b: '
    )
    toggle_array = 'a' in user
    toggle_battery = 'b' in user
    if toggle_array or toggle_battery:
        with environment.contexts() as ctx:
            ctx.power_array_relay_status_input ^= toggle_array
            ctx.power_battery_relay_status ^= toggle_battery
