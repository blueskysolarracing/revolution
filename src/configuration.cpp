#include <functional>
#include <string>
#include <vector>

#include "configuration.h"

namespace Revolution {
	Header_space::Header_space(
		const std::string& abort,
		const std::string& exit,
		const std::string& get,
		const std::string& key,
		const std::string& response,
		const std::string& set,
		const std::string& status
	) : abort{abort},
	    exit{exit},
	    get{get},
	    key{key},
	    response{response},
	    set{set},
	    status{status} {}

	const std::string& Header_space::get_abort() const {
		return abort;
	}

	const std::string& Header_space::get_exit() const {
		return exit;
	}

	const std::string& Header_space::get_get() const {
		return get;
	}

	const std::string& Header_space::get_key() const {
		return key;
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

	Topology::Topology(
		const std::string& database,
		const std::string& replica,
		const std::string& hardware,
		const std::string& display
	) : database{database},
	    replica{replica},
	    hardware{hardware},
	    display{display} {}

	const std::string& Topology::get_database() const {
		return database;
	}

	const std::string& Topology::get_replica() const {
		return replica;
	}

	const std::string& Topology::get_hardware() const {
		return hardware;
	}

	const std::string& Topology::get_display() const {
		return display;
	}

	const std::vector<std::reference_wrapper<const std::string>>
		Topology::get_applications() const {
		return {
			get_database(),
			get_replica(),
			get_hardware(),
			get_display()
		};
	}
}
