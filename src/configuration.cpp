#include <functional>
#include <string>
#include <vector>

#include "configuration.h"

namespace Revolution {
	Header_space::Header_space(
		const std::string& abort,
		const std::string& exit,
		const std::string& get,
		const std::string& gpio,
		const std::string& key,
		const std::string& pwm,
		const std::string& response,
		const std::string& set,
		const std::string& spi,
		const std::string& status,
		const std::string& uart
	) : abort{abort},
	    exit{exit},
	    get{get},
	    gpio{gpio},
	    key{key},
	    pwm{pwm},
	    response{response},
	    set{set},
	    spi{spi},
	    status{status},
	    uart{uart} {}

	const std::string& Header_space::get_abort() const {
		return abort;
	}

	const std::string& Header_space::get_exit() const {
		return exit;
	}

	const std::string& Header_space::get_get() const {
		return get;
	}

	const std::string& Header_space::get_gpio() const {
		return gpio;
	}

	const std::string& Header_space::get_key() const {
		return key;
	}

	const std::string& Header_space::get_pwm() const {
		return pwm;
	}

	const std::string& Header_space::get_response() const {
		return response;
	}

	const std::string& Header_space::get_set() const {
		return set;
	}

	const std::string& Header_space::get_spi() const {
		return spi;
	}

	const std::string& Header_space::get_status() const {
		return status;
	}

	const std::string& Header_space::get_uart() const {
		return uart;
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
		Topology::get_peripherals() const {
		return {
			get_display()
		};
	}
}
