#include "topology.h"

namespace Revolution {
	Instance::Instance(
		const std::string &name,
		const unsigned int &priority,
		const Log_level &log_level,
		const std::string &log_filename,
		const std::string &command
	) : name{name},
	    priority{priority},
	    log_level{log_level},
	    log_filename{log_filename},
	    command{command}
	{
	}

	const std::string &Instance::get_name() const
	{
		return name;
	}

	const unsigned int &Instance::get_priority() const
	{
		return priority;
	}

	const Log_level &Instance::get_log_level() const
	{
		return log_level;
	}

	const std::string &Instance::get_log_filename() const
	{
		return log_filename;
	}

	const std::string &Instance::get_command() const
	{
		return command;
	}

	Topology::Topology()
		: syncer{
			"syncer",
			0,
			Log_level::info,
			"syncer.log",
			"./syncer"
		}, display_driver{
			"display_driver",
			0,
			Log_level::info,
			"display_driver.log",
			"./display_driver"
		}, miscellanious_controller{
			"miscellanious_controller",
			0,
			Log_level::info,
			"miscellanious_controller.log",
			"./miscellanious_controller"
		}, motor_controller{
			"motor_controller",
			0,
			Log_level::info,
			"motor_controller.log",
			"./motor_controller"
		}, power_sensor{
			"power_sensor",
			0,
			Log_level::info,
			"power_sensor.log",
			"./power_sensor"
		}, telemeter{
			"telemeter",
			0,
			Log_level::info,
			"telemeter.log",
			"./telemeter"
		}, voltage_controller{
			"voltage_controller",
			0,
			Log_level::info,
			"voltage_controller.log",
			"./voltage_controller"
		}
	{
	}

	const Instance &Topology::get_syncer() const
	{
		return syncer;
	}

	const Instance &Topology::get_display_driver() const
	{
		return display_driver;
	}

	const Instance &Topology::get_miscellanious_controller() const
	{
		return miscellanious_controller;
	}

	const Instance &Topology::get_motor_controller() const
	{
		return motor_controller;
	}

	const Instance &Topology::get_power_sensor() const
	{
		return power_sensor;
	}

	const Instance &Topology::get_telemeter() const
	{
		return telemeter;
	}

	const Instance &Topology::get_voltage_controller() const
	{
		return voltage_controller;
	}

	const Instance &Topology::get_master() const
	{
		return get_syncer();
	}

	std::vector<Instance> Topology::get_slaves() const
	{
		return {
			get_display_driver(),
			get_miscellanious_controller(),
			get_motor_controller(),
			get_power_sensor(),
			get_telemeter(),
			get_voltage_controller()
		};
	}
}
