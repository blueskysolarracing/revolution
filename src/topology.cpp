#include "topology.h"

namespace Revolution {
	Topology::Endpoint::Endpoint(
		const std::string& name,
		const Logger::Configuration& logger_configuration,
		const Messenger::Configuration& messenger_configuration,
		const std::string& binary_filename
	) : name{name},
	    logger_configuration{logger_configuration},
	    messenger_configuration{messenger_configuration},
	    binary_filename{binary_filename}
	{
	}

	std::string Topology::Endpoint::get_command() const
	{
		return binary_filename + " &";
	}

	Topology::Topology(
		const Endpoint& syncer,
		const Endpoint& display_driver,
		const Endpoint& miscellaneous_controller,
		const Endpoint& motor_controller,
		const Endpoint& power_sensor,
		const Endpoint& telemeter,
		const Endpoint& voltage_controller,
		const Endpoint& watchdog
	) : syncer{syncer},
	    display_driver{display_driver},
	    miscellaneous_controller{miscellaneous_controller},
	    motor_controller{motor_controller},
	    power_sensor{power_sensor},
	    telemeter{telemeter},
	    voltage_controller{voltage_controller},
	    watchdog{watchdog}
	{
	}

	const Topology::Endpoint& Topology::get_master() const
	{
		return syncer;
	}

	const std::vector<Topology::Endpoint> Topology::get_slaves() const
	{
		return {
			display_driver,
			miscellaneous_controller,
			motor_controller,
			power_sensor,
			telemeter,
			voltage_controller,
			watchdog
		};
	}

	const std::vector<Topology::Endpoint> Topology::get_endpoints() const
	{
		std::vector<Topology::Endpoint> endpoints = get_slaves();
		endpoints.push_back(get_master());

		return endpoints;
	}

	Header_space::Header_space(
		const std::string& status,
		const std::string& get,
		const std::string& set,
		const std::string& reset,
		const std::string& sync,
		const std::string& exit,
		const std::string& response
	) : status{status},
	    get{get},
	    set{set},
	    reset{reset},
	    sync{sync},
	    exit{exit},
	    response{response}
	{
	}

	Key_space::Key_space(
		const std::string& heartbeat_suffix
	) : heartbeat_suffix{heartbeat_suffix}
	{
	}

	std::string Key_space::get_heartbeat(const std::string& name) const
	{
		return name + heartbeat_suffix;
	}
}
