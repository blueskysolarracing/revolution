from time import sleep

while True:
    with environment.contexts() as ctx:
        print(
            f"L:{ctx.miscellaneous_left_wheel_accelerations} | "
            f"R:{ctx.miscellaneous_right_wheel_accelerations}"
        )
    sleep(0.5)