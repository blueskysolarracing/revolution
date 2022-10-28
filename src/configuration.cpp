#include <string>
#include <vector>

#include "configuration.h"

namespace Revolution {
	Topology::Endpoint::Endpoint(const std::string& name) : name{name}
	{
	}

	Topology::Topology(
		const Endpoint& display_driver,
		const Endpoint& miscellaneous_controller,
		const Endpoint& motor_controller,
		const Endpoint& power_sensor,
		const Endpoint& replica,
		const Endpoint& syncer,
		const Endpoint& telemeter,
		const Endpoint& voltage_controller
	) : display_driver{display_driver},
	    miscellaneous_controller{miscellaneous_controller},
	    motor_controller{motor_controller},
	    power_sensor{power_sensor},
	    replica{replica},
	    syncer{syncer},
	    telemeter{telemeter},
	    voltage_controller{voltage_controller}
	{
	}

	const Topology::Endpoint& Topology::get_marshal() const
	{
		return syncer;
	}

	const std::vector<Topology::Endpoint> Topology::get_soldiers() const
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

	Header_space::Header_space(
		const std::string& exit,
		const std::string& get,
		const std::string& hang,
		const std::string& heartbeat,
		const std::string& reset,
		const std::string& response,
		const std::string& set,
		const std::string& status,
		const std::string& sync
	) : exit{exit},
	    get{get},
	    hang{hang},
	    heartbeat{heartbeat},
	    reset{reset},
	    response{response},
	    set{set},
	    status{status},
	    sync{sync}
	{
	}
}
