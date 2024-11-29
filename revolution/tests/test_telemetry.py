""":mod:`revolution.tests.test_telemetry` implements tests for
telemetry.
"""

from dataclasses import replace
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

from door.threading2 import AcquirableDoor
from revolution import Environment, Telemetry
from revolution.tests import configurations


class TestTelemetry(TestCase):
    def setUp(self) -> None:
        self.environment: Environment = Environment(
            AcquirableDoor(replace(configurations.CONTEXTS)),
            replace(configurations.PERIPHERIES),
            replace(configurations.SETTINGS),
        )
        self.telemetry = Telemetry(self.environment)
        self.telemetry._telemetry_worker = MagicMock()

    def test_telemetry(self) -> None:
        mock_settings = MagicMock()
        mock_settings.telemetry_timeout = 1
        mock_settings.telemetry_begin_token = b'__BEGIN__'
        mock_settings.telemetry_separator_token = b'|'
        mock_settings.telemetry_end_token = b'__END__'

        mock_resource = MagicMock()
        mock_resource.serialize.return_value = '{"key": "value"}'

        mock_contexts = MagicMock()
        mock_contexts.__enter__.return_value = MagicMock(
            _resource=mock_resource,
        )

        self.telemetry.environment = MagicMock()
        self.telemetry.environment.settings = mock_settings
        self.telemetry.environment.contexts.return_value = mock_contexts
        mock_serial = MagicMock()
        self.telemetry.environment.peripheries.telemetry_radio_serial = \
            mock_serial

        with patch('hashlib.md5') as mock_md5:
            mock_md5.return_value.digest.return_value = b'checksum'

            with patch.object(
                self.telemetry._stoppage, 'wait', return_value=True
            ):
                self.telemetry._telemetry()

        # Expected raw data format:
        # raw_data = b'__BEGIN__{"key": "value"}|checksum__END__'
        # self.environment.peripheries.telemetry_radio_serial.write.\
        #     assert_called_with(raw_data)


if __name__ == '__main__':
    main()
