#ifndef REVOLUTION_TOPOLOGY_H
#define REVOLUTION_TOPOLOGY_H

#include <vector>

#include "logger.h"

namespace Revolution {
	class Instance {
	public:
		explicit Instance(
			const std::string &name,
			const unsigned int &priority,
			const Log_level &log_level,
			const std::string &log_filename,
			const std::string &command
		);

		const std::string &get_name() const;
		const unsigned int &get_priority() const;
		const Log_level &get_log_level() const;
		const std::string &get_log_filename() const;
		const std::string &get_command() const;
	private:
		const std::string name;
		const unsigned int priority;
		const Log_level log_level;
		const std::string log_filename;
		const std::string command;
	};

	class Topology {
	public:
		Topology();

		const Instance &get_syncer() const;
		const Instance &get_display_driver() const;
		const Instance &get_miscellanious_controller() const;
		const Instance &get_motor_controller() const;
		const Instance &get_power_sensor() const;
		const Instance &get_telemeter() const;
		const Instance &get_voltage_controller() const;

		const Instance &get_master() const;
		std::vector<Instance> get_slaves() const;
	private:
		const Instance syncer;
		const Instance display_driver;
		const Instance miscellanious_controller;
		const Instance motor_controller;
		const Instance power_sensor;
		const Instance telemeter;
		const Instance voltage_controller;
	};
};

#endif  // REVOLUTION_TOPOLOGY_H
