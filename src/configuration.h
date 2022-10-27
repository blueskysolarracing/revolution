#ifndef REVOLUTION_CONFIGURATION_H
#define REVOLUTION_CONFIGURATION_H

#include <string>
#include <vector>

namespace Revolution {
	struct Topology {
		struct Endpoint {
			explicit Endpoint(const std::string& name);

			const std::string name;
		};

		explicit Topology(
			const Endpoint& syncer = Endpoint{"syncer"},
			const Endpoint& display_driver
				= Endpoint{"display_driver"},
			const Endpoint& miscellaneous_controller
				= Endpoint{"miscellaneous_controller"},
			const Endpoint& motor_controller
				= Endpoint{"motor_controller"},
			const Endpoint& power_sensor = Endpoint{"power_sensor"},
			const Endpoint& replica = Endpoint{"replica"},
			const Endpoint& telemeter = Endpoint{"telemeter"},
			const Endpoint& voltage_controller
				= Endpoint{"voltage_controller"}
		);

		const Endpoint& get_master() const;
		const std::vector<Endpoint> get_slaves() const;
		const std::vector<Endpoint> get_endpoints() const;

		const Endpoint syncer;
		const Endpoint display_driver;
		const Endpoint miscellaneous_controller;
		const Endpoint motor_controller;
		const Endpoint power_sensor;
		const Endpoint replica;
		const Endpoint telemeter;
		const Endpoint voltage_controller;
	};

	struct Header_space {
		explicit Header_space(
			const std::string& status = "STATUS",
			const std::string& get = "GET",
			const std::string& set = "SET",
			const std::string& reset = "RESET",
			const std::string& sync = "SYNC",
			const std::string& hang = "HANG",
			const std::string& exit = "EXIT",
			const std::string& response = "RESPONSE"
		);

		const std::string status;
		const std::string get;
		const std::string set;
		const std::string reset;
		const std::string sync;
		const std::string hang;
		const std::string exit;
		const std::string response;
	};

	struct Key_space {
	};
};

#endif  // REVOLUTION_CONFIGURATION_H

