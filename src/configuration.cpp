#include <string>
#include <vector>

#include "configuration.h"

namespace Revolution {
	Topology::Endpoint::Endpoint(const std::string& name) : name{name}
	{
	}

	Topology::Topology(
		const Endpoint& syncer,
		const Endpoint& display_driver,
		const Endpoint& miscellaneous_controller,
		const Endpoint& motor_controller,
		const Endpoint& power_sensor,
		const Endpoint& replica,
		const Endpoint& telemeter,
		const Endpoint& voltage_controller
	) : syncer{syncer},
	    display_driver{display_driver},
	    miscellaneous_controller{miscellaneous_controller},
	    motor_controller{motor_controller},
	    power_sensor{power_sensor},
	    replica{replica}
	    telemeter{telemeter},
	    voltage_controller{voltage_controller},
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
			replica,
			telemeter,
			voltage_controller
		};
	}

	const std::vector<Topology::Endpoint> Topology::get_endpoints() const
	{
		auto endpoints = get_slaves();
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
}

