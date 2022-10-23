#include <fcntl.h>

#include "configuration.h"

namespace Revolution {
	Configuration::Applications::Parameters::Parameters(
		const Logger::Severity& logger_severity,
		const std::string& logger_filename,
		const std::ofstream::openmode& logger_open_mode,
		const std::string& messenger_name,
		const int& messenger_oflags,
		const mode_t& messenger_mode,
		const unsigned int& messenger_priority,
		const bool& messenger_unlink_status,
		const std::string& pid_filename,
		const std::string& binary_filename
	) : logger_severity{logger_severity},
	    logger_filename{logger_filename},
	    logger_open_mode{logger_open_mode},
	    messenger_name{messenger_name},
	    messenger_oflags{messenger_oflags},
	    messenger_mode{messenger_mode},
	    messenger_priority{messenger_priority},
	    messenger_unlink_status{messenger_unlink_status},
	    pid_filename{pid_filename},
	    binary_filename{binary_filename}
	{
	}

	Configuration::Applications::Applications(
		const Parameters& syncer,
		const Parameters& display_driver,
		const Parameters& miscellaneous_controller,
		const Parameters& motor_controller,
		const Parameters& power_sensor,
		const Parameters& telemeter,
		const Parameters& voltage_controller
	) : syncer{syncer},
	    display_driver{display_driver},
	    miscellaneous_controller{miscellaneous_controller},
	    motor_controller{motor_controller},
	    power_sensor{power_sensor},
	    telemeter{telemeter},
	    voltage_controller{voltage_controller}
	{
	}

	Configuration::Headers::Headers(
		const std::string& get_command,
		const std::string& set_command,
		const std::string& exit_command,
		const std::string& state_broadcast
	) : get_command{get_command},
	    set_command{set_command},
	    exit_command{exit_command},
	    state_broadcast{state_broadcast}
	{
	}

	Configuration::Configuration()
		: applications{
			Applications::Parameters{
				Logger::info,
				"./syncer.log",
				std::ofstream::app,
				"/revolution_syncer",
				O_RDWR | O_CREAT,
				0644,
				0,
				true,
				"./syncer.pid",
				"./syncer"
			},
			Applications::Parameters{
				Logger::info,
				"./display_driver.log",
				std::ofstream::app,
				"/revolution_display_driver",
				O_RDWR | O_CREAT,
				0644,
				0,
				true,
				"./display_driver.pid",
				"./display_driver"
			},
			Applications::Parameters{
				Logger::info,
				"./miscellaneous_controller.log",
				std::ofstream::app,
				"/revolution_miscellaneous_controller",
				O_RDWR | O_CREAT,
				0644,
				0,
				true,
				"./miscellaneous_controller.pid",
				"./miscellaneous_controller"
			},
			Applications::Parameters{
				Logger::info,
				"./motor_controller.log",
				std::ofstream::app,
				"/revolution_motor_controller",
				O_RDWR | O_CREAT,
				0644,
				0,
				true,
				"./motor_controller.pid",
				"./motor_controller"
			},
			Applications::Parameters{
				Logger::info,
				"./power_sensor.log",
				std::ofstream::app,
				"/revolution_power_sensor",
				O_RDWR | O_CREAT,
				0644,
				0,
				true,
				"./power_sensor.pid",
				"./power_sensor"
			},
			Applications::Parameters{
				Logger::info,
				"./telemeter.log",
				std::ofstream::app,
				"/revolution_telemeter",
				O_RDWR | O_CREAT,
				0644,
				0,
				true,
				"./telemeter.pid",
				"./telemeter"
			},
			Applications::Parameters{
				Logger::info,
				"./voltage_controller.log",
				std::ofstream::app,
				"/revolution_voltage_controller",
				O_RDWR | O_CREAT,
				0644,
				0,
				true,
				"./voltage_controller.pid",
				"./voltage_controller"
			}
		  }, headers {
			"GET",
			"SET",
			"EXIT",
			"STATE_BROADCAST"
		  }
	{
	}
}
