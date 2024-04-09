from math import inf
from time import sleep, time
from typing import Any, cast
import unittest
from unittest.mock import call, Default, MagicMock, patch
from driver import Driver
from revolution.utilities import Direction
from environment import Contexts, Settings, Peripheries



class TestDriver(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()
        self.peripheries = Peripheries()
        self.driver = Driver(settings=self.settings, peripheries=self.peripheries)

    def test_teardown(self):
        self.driver._driver_worker.start = MagicMock()
        self.driver._driver_worker.join = MagicMock()
      
        self.driver._setup()
        self.driver._driver_worker.start.assert_called_once()

        self.driver._teardown()
        self.driver._driver_worker.join.assert_called_once()

    # patch being used to mock time.sleep() and time.time()
    @patch('time.sleep', MagicMock())
  
    # To mock time related behaviour in tests
    @patch('time.time', MagicMock(side_effect=[1, 2, 3]))
  
    def test_driver(self):
        # Mock environment settings
        self.settings.driver_timeout = 5

        # Mock peripheries
        self.peripheries.driver_mcp23s17.read_register.side_effect = [(1,), (2,)]
        self.peripheries.driver_adc78h89.sample_all.return_value = {
            'driver_motor_acceleration_pedal_input_channel': 0.5,
            'driver_motor_regeneration_pedal_input_channel': 0.2,
            'driver_motor_acceleration_paddle_input_channel': 0.8,
            'driver_motor_regeneration_paddle_input_channel': 0.3,
            'driver_miscellaneous_thermistor_input_channel': 24.0
        }

        # Mock previous state of GPIO
        previous_lookup = {(1, 0, 0): False, (1, 0, 1): False, (1, 0, 2): False,
                           (1, 0, 3): False, (1, 0, 4): False, (1, 0, 5): False,
                           (1, 0, 6): False, (1, 0, 7): False,
                           (1, 1, 0): False, (1, 1, 1): False, (1, 1, 2): False,
                           (1, 1, 3): False, (1, 1, 4): False, (1, 1, 5): False,
                           (1, 1, 6): False, (1, 1, 7): False}

        stoppage_mock = MagicMock()
        self.driver._stoppage = stoppage_mock
        stoppage_mock.wait.side_effect = [False, True]

        # Calling driver
        self.driver._driver()

        # Assert GPIO read_register is called twice
        self.assertEqual(self.peripheries.driver_mcp23s17.read_register.call_count, 2)

        # Assert context attributes are set correctly
        self.assertEqual(self.driver.contexts.motor_acceleration_pedal_input, 0.5)
        self.assertEqual(self.driver.contexts.motor_regeneration_pedal_input, 0.2)
        self.assertEqual(self.driver.contexts.motor_acceleration_paddle_input, 0.8)
        self.assertEqual(self.driver.contexts.motor_regeneration_paddle_input, 0.3)
        self.assertEqual(self.driver.contexts.miscellaneous_thermistor_temperature, 24.0)

        # Assert momentary/toggling/additive switches


if __name__ == '__main__':
    unittest.main()
