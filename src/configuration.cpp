#include <functional>
#include <string>
#include <vector>

#include "configuration.h"

namespace Revolution {
	Header_space::Header_space(
		const std::string& abort,
		const std::string& data,
		const std::string& exit,
		const std::string& response,
		const std::string& state,
		const std::string& status
	) : abort{abort},
	    data{data},
	    exit{exit},
	    response{response},
	    state{state},
	    status{status} {}

	const std::string& Header_space::get_abort() const {
		return abort;
	}

	const std::string& Header_space::get_data() const {
		return data;
	}

	const std::string& Header_space::get_exit() const {
		return exit;
	}

	const std::string& Header_space::get_response() const {
		return response;
	}

	const std::string& Header_space::get_state() const {
		return state;
	}

	const std::string& Header_space::get_status() const {
		return status;
	}

	Topology::Topology(
		const std::string& database,
		const std::string& replica,
		const std::string& display
	) : database{database},
	    replica{replica},
	    display{display} {}

	const std::string& Topology::get_database() const {
		return database;
	}

	const std::string& Topology::get_replica() const {
		return replica;
	}

	const std::string& Topology::get_display() const {
		return display;
	}

	const std::vector<std::reference_wrapper<const std::string>>
		Topology::get_peripherals() const {
		return {
			get_display()
		};
	}
}
