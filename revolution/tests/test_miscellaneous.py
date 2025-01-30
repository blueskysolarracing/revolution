from dataclasses import replace
from threading import Thread
from time import sleep
from typing import ClassVar
from unittest import TestCase, main

from door.threading2 import AcquirableDoor
from revolution.miscellaneous import Miscellaneous
from revolution.environment import Environment, Header, Message
from revolution.tests import configurations


class MiscellaneousTestCase(TestCase):
    TIMEOUT: ClassVar[float] = 0.1

    def setUp(self) -> None:
        self.environment = Environment(
            AcquirableDoor(
                replace(configurations.CONTEXTS)
            ),
            replace(configurations.PERIPHERIES),
            replace(configurations.SETTINGS),
        )
        self.miscellaneous_thread = Thread(
            target=Miscellaneous.main,
            args=(self.environment,),
        )
        self.miscellaneous_thread.start()
        sleep(self.TIMEOUT)

    def tearDown(self) -> None:
        self.environment.send_all(Message(Header.STOP))
        self.miscellaneous_thread.join()

    def test_left_indicator_light(self) -> None:
        with self.environment.contexts() as contexts:
            contexts.miscellaneous_left_indicator_light_status_input = True

        sleep(self.TIMEOUT)

        (
            self
            .environment
            .peripheries
            .miscellaneous_left_indicator_light_pwm
            .enable
            .assert_called_once()
        )

        with self.environment.contexts() as contexts:
            contexts.miscellaneous_left_indicator_light_status_input = False

        sleep(self.TIMEOUT)

        (
            self
            .environment
            .peripheries
            .miscellaneous_left_indicator_light_pwm
            .disable
            .assert_called_once()
        )

    def test_right_indicator_light(self) -> None:
        with self.environment.contexts() as contexts:
            contexts.miscellaneous_right_indicator_light_status_input = True

        sleep(self.TIMEOUT)

        (
            self
            .environment
            .peripheries
            .miscellaneous_right_indicator_light_pwm
            .enable
            .assert_called_once()
        )

        with self.environment.contexts() as contexts:
            contexts.miscellaneous_right_indicator_light_status_input = False

        sleep(self.TIMEOUT)

        (
            self
            .environment
            .peripheries
            .miscellaneous_right_indicator_light_pwm
            .disable
            .assert_called_once()
        )

    def test_daytime_running_lights(self) -> None:
        with self.environment.contexts() as contexts:
            contexts.miscellaneous_daytime_running_lights_status_input = True
    
        sleep(self.TIMEOUT)

        (
            self.environment.peripheries
            .miscellaneous_daytime_running_lights_pwm
            .enable
            .assert_called_once()
        )

        with self.environment.contexts() as contexts:
            contexts.miscellaneous_daytime_running_lights_status_input = False

        sleep(self.TIMEOUT)

        (
            self.environment.peripheries
            .miscellaneous_daytime_running_lights_pwm
            .disable
            .assert_called_once()
        )

    def test_break_lights(self) -> None:
        with self.environment.contexts() as contexts:
            contexts.miscellaneous_brake_status_input = True
        sleep(self.TIMEOUT)

        (
            self.environment.peripheries
            .miscellaneous_brake_lights_pwm
            .enable
            .assert_called_once()
        )

        with self.environment.contexts() as contexts:
            contexts.miscellaneous_brake_status_input = False

        sleep(self.TIMEOUT)

        (
            self.environment.peripheries
            .miscellaneous_brake_lights_pwm
            .disable
            .assert_called_once()
        )


if __name__ == "__main__":
    main()  # pragma: no cover
