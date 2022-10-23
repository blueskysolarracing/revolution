#include "configuration.h"

namespace Revolution {
	Configuration::Applications::Parameters::Parameters(
		const std::string& name,
		const unsigned int& priority,
		const Logger::Severity& log_severity,
		const std::string& log_filename,
		const std::ofstream::openmode& log_open_mode,
		const std::string& pid_filename,
		const std::string& binary_filename
	) : name{name},
	    priority{priority},
	    log_severity{log_severity},
	    log_filename{log_filename},
	    log_open_mode{log_open_mode},
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
				"syncer",
				0,
				Logger::info,
				"./syncer.log",
				std::ofstream::app,
				"./syncer.pid",
				"./syncer"
			},
			Applications::Parameters{
				"display_driver",
				0,
				Logger::info,
				"./display_driver.log",
				std::ofstream::app,
				"./display_driver.pid",
				"./display_driver"
			},
			Applications::Parameters{
				"miscellaneous_controller",
				0,
				Logger::info,
				"./miscellaneous_controller.log",
				std::ofstream::app,
				"./miscellaneous_controller.pid",
				"./miscellaneous_controller"
			},
			Applications::Parameters{
				"motor_controller",
				0,
				Logger::info,
				"./motor_controller.log",
				std::ofstream::app,
				"./motor_controller.pid",
				"./motor_controller"
			},
			Applications::Parameters{
				"power_sensor",
				0,
				Logger::info,
				"./power_sensor.log",
				std::ofstream::app,
				"./power_sensor.pid",
				"./power_sensor"
			},
			Applications::Parameters{
				"telemeter",
				0,
				Logger::info,
				"./telemeter.log",
				std::ofstream::app,
				"./telemeter.pid",
				"./telemeter"
			},
			Applications::Parameters{
				"voltage_controller",
				0,
				Logger::info,
				"./voltage_controller.log",
				std::ofstream::app,
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
