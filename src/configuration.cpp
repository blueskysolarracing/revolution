#include <functional>
#include <string>
#include <vector>

#include "configuration.h"

namespace Revolution {
	Header_space::Header_space(
		const std::string& abort_header,
		const std::string& data_header,
		const std::string& exit_header,
		const std::string& response_header,
		const std::string& state_header,
		const std::string& status_header
	) : abort_header{abort_header},
	    data_header{data_header},
	    exit_header{exit_header},
	    response_header{response_header},
	    state_header{state_header},
	    status_header{status_header} {}

	const std::string& Header_space::get_abort_header() const {
		return abort_header;
	}

	const std::string& Header_space::get_data_header() const {
		return data_header;
	}

	const std::string& Header_space::get_exit_header() const {
		return exit_header;
	}

	const std::string& Header_space::get_response_header() const {
		return response_header;
	}

	const std::string& Header_space::get_state_header() const {
		return state_header;
	}

	const std::string& Header_space::get_status_header() const {
		return status_header;
	}

	Topology::Topology(
		const std::string& database_name,
		const std::string& replica_name,
		const std::string& display_name
	) : database_name{database_name},
	    replica_name{replica_name},
	    display_name{display_name} {}

	const std::string& Topology::get_database_name() const {
		return database_name;
	}

	const std::string& Topology::get_replica_name() const {
		return replica_name;
	}

	const std::string& Topology::get_display_name() const {
		return display_name;
	}

	const std::vector<std::reference_wrapper<const std::string>>
		Topology::get_peripheral_names() const {
		return {
			get_display_name()
		};
	}
}
