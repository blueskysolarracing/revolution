from dataclasses import dataclass, field
from threading import Thread
from typing import Any, ClassVar
from unittest import main, Testcase

from revolution.application import Application
from revolution.environment import (
    Environment, 
    Header, 
    Message, 
    Endpoint, 
    Contexts,
)

@dataclass
class Debugger(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.DEBUGGER
    mainloop_flag: bool = field(default=False, init=False)
    setup_flag: bool = field(default=False, init=False)
    run_flag: bool = field(default=False, init=False)
    teardown_flag: bool = field(default=False, init=False)
    debug_flag: bool = field(default=False, init=False)
    debug_args: tuple[Any, ...] = field(default=(), init=False)
    debug_kwargs: dict[str, Any] = field(default_factory=dict, init=False)

    def mainloop(self) -> None:
        super().mainloop()
        self.mainloop_flag = True

    def _setup(self) -> None:
        super()._setup()
        self._handlers[Header.DEBUG] = self.__handle_debug
        self.setup_flag = True

    def _run(self) -> None:
        super()._run()
        self.run_flag = True

    def _teardown(self) -> None:
        self.teardown_flag = True
        super()._teardown()

    def __handle_debug(self, /, *args: Any, **kwargs: Any) -> None:
        self.debug_flag = True
        self.debug_args += args
        self.debug_kwargs |= kwargs


class ApplicationTestCase(TestCase):
    def test_mainloop(self):
        context = Contexts(display_backup_camera_control_status_input=False,
                           display_steering_wheel_in_place_status_input=False,
                           display_left_directional_pad_input=False,
                           display_right_directional_pad_input=False,
                           display_up_directional_pad_input=False,
                           display_down_directional_pad_input=False,
                           display_center_directional_pad_input=False,
                           miscellaneous_thermistor_temperature=0,
                           miscellaneous_left_indicator_light_status_input=False,
                           miscellaneous_right_indicator_light_status_input=False,
                           miscellaneous_hazard_lights_status_input=False,
                           miscellaneous_daytime_running_lights_status_input=False,
                           miscellaneous_horn_status_input=False,
                           miscellaneous_fan_status_input=False,
                           miscellaneous_brake_status_input=False,
                           motor_acceleration_pedal_input=0,
                           motor_regeneration_pedal_input=0,
                           motor_acceleration_paddle_input=0,
                           motor_regeneration_paddle_input=0,
                           motor_status_input=False,
                           motor_direction_input=0,
                           motor_economical_mode_input=True,
                           motor_variable_field_magnet_up_input=0,
                           motor_variable_field_magnet_down_input=0,
                           motor_revolution_period=float('inf'),
                           motor_speed=0,
                           power_array_relay_status_input=False,
                           power_battery_relay_status_input=False)
        environment = Environment(contexts=context, peripheries = None, settings = None)
        debugger = Debugger(environment)
        thread = Thread(target=debugger.mainloop)

        self.assertFalse(debugger.mainloop_flag)
        self.assertFalse(debugger.setup_flag)
        self.assertFalse(debugger.run_flag)
        self.assertFalse(debugger.teardown_flag)
        self.assertFalse(debugger.debug_flag)
        thread.start()
        environment.send(debugger.endpoint, Message(Header.STOP))
        thread.join()
        self.assertTrue(debugger.mainloop_flag)
        self.assertTrue(debugger.setup_flag)
        self.assertTrue(debugger.run_flag)
        self.assertTrue(debugger.teardown_flag)
        self.assertFalse(debugger.debug_flag)

    def test_run(self):
        context = Contexts(display_backup_camera_control_status_input=False,
                           display_steering_wheel_in_place_status_input=False,
                           display_left_directional_pad_input=False,
                           display_right_directional_pad_input=False,
                           display_up_directional_pad_input=False,
                           display_down_directional_pad_input=False,
                           display_center_directional_pad_input=False,
                           miscellaneous_thermistor_temperature=0,
                           miscellaneous_left_indicator_light_status_input=False,
                           miscellaneous_right_indicator_light_status_input=False,
                           miscellaneous_hazard_lights_status_input=False,
                           miscellaneous_daytime_running_lights_status_input=False,
                           miscellaneous_horn_status_input=False,
                           miscellaneous_fan_status_input=False,
                           miscellaneous_brake_status_input=False,
                           motor_acceleration_pedal_input=0,
                           motor_regeneration_pedal_input=0,
                           motor_acceleration_paddle_input=0,
                           motor_regeneration_paddle_input=0,
                           motor_status_input=False,
                           motor_direction_input=0,
                           motor_economical_mode_input=True,
                           motor_variable_field_magnet_up_input=0,
                           motor_variable_field_magnet_down_input=0,
                           motor_revolution_period=float('inf'),
                           motor_speed=0,
                           power_array_relay_status_input=False,
                           power_battery_relay_status_input=False)
        environment = Environment(contexts=context, peripheries = None, settings = None)
        debugger = Debugger(environment)
        thread = Thread(target=debugger.mainloop)

        self.assertFalse(debugger.debug_flag)
        self.assertEqual(debugger.debug_args, ())
        self.assertEqual(debugger.debug_kwargs, {})
        thread.start()
        environment.send(
            debugger.endpoint,
            Message(Header.DEBUG, (0, 1), {'hello': 'world'}),
        )
        environment.send(
            debugger.endpoint,
            Message(Header.DEBUG, (2,)),
        )
        environment.send(
            debugger.endpoint,
            Message(Header.STOP)
        )
        thread.join()
        self.assertTrue(debugger.debug_flag)
        self.assertTupleEqual(debugger.debug_args, (0, 1, 2))
        self.assertDictEqual(debugger.debug_kwargs, {'hello': 'world'})


if __name__ == '__main__':
    main()
