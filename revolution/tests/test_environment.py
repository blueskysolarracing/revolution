import unittest
from dataclasses import replace
from door.threading2 import AcquirableDoor
from revolution.utilities import Direction
from revolution.tests import configurations
from revolution.environment import (
    Environment,
    Header,
    Message,
    Contexts,
    Settings
)


class TestSerialization(unittest.TestCase):

    @staticmethod
    def create_sample_contexts() -> Contexts:
        """Helper function to generate sample Contexts for testing."""
        return Contexts(
            miscellaneous_left_indicator_light_status_input=True,
            miscellaneous_right_indicator_light_status_input=False,
            miscellaneous_hazard_lights_status_input=True,
            miscellaneous_daytime_running_lights_status_input=False,
            miscellaneous_horn_status_input=True,
            miscellaneous_backup_camera_control_status_input=False,
            miscellaneous_display_backlight_status_input=True,
            miscellaneous_brake_status_input=False,
            motor_acceleration_input=1.0,
            motor_regeneration_input=0.5,
            motor_cruise_control_acceleration_input=0.3,
            motor_cruise_control_regeneration_input=0.2,
            motor_status_input=True,
            motor_direction_input=Direction.FORWARD,
            motor_economical_mode_input=False,
            motor_variable_field_magnet_up_input=2,
            motor_variable_field_magnet_down_input=1,
            motor_speed=100.5,
            motor_cruise_control_status_input=True,
            motor_cruise_control_speed=50.0,
            power_array_relay_status_input=True,
            power_battery_relay_status_input=False,
            power_state_of_charge=75.0,
        )

    @staticmethod
    def create_sample_settings() -> Settings:
        """Helper function to generate sample Settings for testing."""
        return Settings(
            display_frame_rate=60.0,
            display_font_pathname="/fonts/sample.ttf",
            driver_timeout=5.0,
            driver_acceleration_input_step=0.1,
            miscellaneous_light_timeout=2.0,
            motor_wheel_circumference=1.5,
            motor_control_timeout=3.0,
            motor_variable_field_magnet_timeout=1.2,
            motor_revolution_timeout=2.5,
            motor_cruise_control_k_p=0.5,
            motor_cruise_control_k_i=0.1,
            motor_cruise_control_k_d=0.05,
            motor_cruise_control_min_integral=-10.0,
            motor_cruise_control_max_integral=10.0,
            motor_cruise_control_min_derivative=-5.0,
            motor_cruise_control_max_derivative=5.0,
            motor_cruise_control_min_output=0.0,
            motor_cruise_control_max_output=1.0,
            motor_cruise_control_timeout=2.0,
            power_monitor_timeout=4.0,
            power_battery_relay_timeout=3.5,
            telemetry_timeout=1.0,
            telemetry_begin_token=b'__BEGIN__',
            telemetry_separator_token=b'__SEPARATOR__',
            telemetry_end_token=b'__END__',
        )

    def test_message_serialization(self) -> None:
        """Test serialization and deserialization of a Message object."""
        msg = Message(
            header=Header.STOP,
            args=(1, 2, 3),
            kwargs={'key': 'value'}
        )
        serialized = msg.serialize()
        deserialized = Message.deserialize(serialized)
        self.assertEqual(
            msg,
            deserialized,
            (
                "Message serialization failed: "
                f"Original={msg}, Deserialized={deserialized}"
            )
        )

    def test_contexts_serialization(self) -> None:
        """Test serialization and deserialization of Contexts."""
        contexts = self.create_sample_contexts()
        serialized = contexts.serialize()
        deserialized = Contexts.deserialize(serialized)
        self.assertEqual(
            contexts,
            deserialized,
            (
                "Contexts serialization failed: "
                f"Original={contexts}, Deserialized={deserialized}"
            )
        )

    def test_settings_serialization(self) -> None:
        """Test serialization and deserialization of Settings."""
        settings = self.create_sample_settings()
        serialized = settings.serialize()
        deserialized = Settings.deserialize(serialized)
        self.assertEqual(
            settings,
            deserialized,
            (
                "Settings serialization failed: "
                f"Original={settings}, Deserialized={deserialized}"
            )
        )

    def test_environment_serialization(self) -> None:
        """Test serialization and deserialization of an Environment object."""
        contexts = AcquirableDoor(self.create_sample_contexts())
        settings = self.create_sample_settings()
        peripheries = replace(configurations.PERIPHERIES)

        env = Environment(
            contexts=contexts,
            peripheries=peripheries,
            settings=settings
        )
        serialized = env.serialize()
        deserialized = Environment.deserialize(serialized)

        self.assertEqual(
            env.settings,
            deserialized.settings,
            (
                "Environment settings serialization failed: "
                f"Original={env.settings}, "
                f"Deserialized={deserialized.settings}"
            )
        )

        self.assertEqual(
            env.contexts,
            deserialized.contexts,
            (
                "Environment contexts serialization failed: "
                f"Original={env.contexts}, "
                f"Deserialized={deserialized.contexts}"
            )
        )


if __name__ == "__main__":
    unittest.main()
