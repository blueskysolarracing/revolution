#include <functional>
#include <string>
#include <vector>

#include "configuration.h"

namespace Revolution {
	Header_space::Header_space(
		const std::string& exit,
		const std::string& get,
		const std::string& reset,
		const std::string& response,
		const std::string& set,
		const std::string& status
	) : exit{exit},
	    get{get},
	    reset{reset},
	    response{response},
	    set{set},
	    status{status} {}

	const std::string& Header_space::get_exit() const {
		return exit;
	}

	const std::string& Header_space::get_get() const {
		return get;
	}

	const std::string& Header_space::get_reset() const {
		return reset;
	}

	const std::string& Header_space::get_response() const {
		return response;
	}

	const std::string& Header_space::get_set() const {
		return set;
	}

	const std::string& Header_space::get_status() const {
		return status;
	}

	Topology::Endpoint::Endpoint(const std::string& name) : name{name} {}

	const std::string& Topology::Endpoint::get_name() const {
		return name;
	}

	Topology::Topology(
		const Endpoint& marshal,
		const Endpoint& display_driver,
		const Endpoint& miscellaneous_controller,
		const Endpoint& motor_controller,
		const Endpoint& power_sensor,
		const Endpoint& replica,
		const Endpoint& telemeter,
		const Endpoint& voltage_controller
	) : marshal{marshal},
	    display_driver{display_driver},
	    miscellaneous_controller{miscellaneous_controller},
	    motor_controller{motor_controller},
	    power_sensor{power_sensor},
	    replica{replica},
	    telemeter{telemeter},
	    voltage_controller{voltage_controller} {}

	const Topology::Endpoint& Topology::get_marshal() const {
		return marshal;
	}

	const Topology::Endpoint& Topology::get_display_driver() const {
		return display_driver;
	}

	const Topology::Endpoint& Topology::get_miscellaneous_controller() const {
		return miscellaneous_controller;
	}

	const Topology::Endpoint& Topology::get_motor_controller() const {
		return motor_controller;
	}

	const Topology::Endpoint& Topology::get_power_sensor() const {
		return power_sensor;
	}

	const Topology::Endpoint& Topology::get_replica() const {
		return replica;
	}

	const Topology::Endpoint& Topology::get_telemeter() const {
		return telemeter;
	}

	const Topology::Endpoint& Topology::get_voltage_controller() const {
		return voltage_controller;
	}

	const std::vector<std::reference_wrapper<const Topology::Endpoint>>
		Topology::get_soldiers() const {
		return {
			get_display_driver(),
			get_miscellaneous_controller(),
			get_motor_controller(),
			get_power_sensor(),
			get_replica(),
			get_telemeter(),
			get_voltage_controller()
		};
	}
}
