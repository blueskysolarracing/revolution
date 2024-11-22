# test_telemetry.py
import unittest
from unittest.mock import MagicMock, patch
from revolution.telemetry import Telemetry

class TestTelemetry(unittest.TestCase):
    def setUp(self):
        self.telemetry = Telemetry()
        self.telemetry._telemetry_worker = MagicMock()

    def test_telemetry(self):
        mock_settings = MagicMock()
        mock_settings.telemetry_timeout = 1
        mock_settings.telemetry_begin_token = b'__BEGIN__'
        mock_settings.telemetry_separator_token = b'|'
        mock_settings.telemetry_end_token = b'__END__'

        mock_resource = MagicMock()
        mock_resource.serialize.return_value = '{"key": "value"}'

        mock_contexts = MagicMock()
        mock_contexts.__enter__.return_value = MagicMock(_resource=mock_resource)

        self.telemetry.environment = MagicMock()
        self.telemetry.environment.settings = mock_settings
        self.telemetry.environment.contexts.return_value = mock_contexts
        self.telemetry.environment.peripheries.telemetry_radio_serial = MagicMock()

        with patch('telemetry.md5') as mock_md5:
            mock_md5.return_value.digest.return_value = b'checksum'

            with patch.object(self.telemetry._stoppage, 'wait', return_value=True):
                self.telemetry._telemetry()

        raw_data = b'__BEGIN__["key": "value"]|checksum__END__'
        self.telemetry.environment.peripheries.telemetry_radio_serial.write.assert_called_with(raw_data)

if __name__ == '__main__':
    unittest.main()
