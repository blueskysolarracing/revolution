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
			const Endpoint& display_driver
				= Endpoint{"display_driver"},
			const Endpoint& miscellaneous_controller
				= Endpoint{"miscellaneous_controller"},
			const Endpoint& motor_controller
				= Endpoint{"motor_controller"},
			const Endpoint& power_sensor = Endpoint{"power_sensor"},
			const Endpoint& replica = Endpoint{"replica"},
			const Endpoint& syncer = Endpoint{"syncer"},
			const Endpoint& telemeter = Endpoint{"telemeter"},
			const Endpoint& voltage_controller
				= Endpoint{"voltage_controller"}
		);

		const Endpoint& get_master() const;
		const std::vector<Endpoint> get_servants() const;

		const Endpoint display_driver;
		const Endpoint miscellaneous_controller;
		const Endpoint motor_controller;
		const Endpoint power_sensor;
		const Endpoint replica;
		const Endpoint syncer;
		const Endpoint telemeter;
		const Endpoint voltage_controller;
	};

	struct Header_space {
		explicit Header_space(
			const std::string& exit = "EXIT",
			const std::string& get = "GET",
			const std::string& hang = "HANG",
			const std::string& heartbeat = "HEARTBEAT",
			const std::string& reset = "RESET",
			const std::string& response = "RESPONSE",
			const std::string& set = "SET",
			const std::string& status = "STATUS",
			const std::string& sync = "SYNC"
		);

		const std::string exit;
		const std::string get;
		const std::string hang;
		const std::string heartbeat;
		const std::string reset;
		const std::string response;
		const std::string set;
		const std::string status;
		const std::string sync;
	};

	struct Key_space {
	};
};

#endif  // REVOLUTION_CONFIGURATION_H
