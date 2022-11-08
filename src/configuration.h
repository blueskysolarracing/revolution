#ifndef REVOLUTION_CONFIGURATION_H
#define REVOLUTION_CONFIGURATION_H

#include <functional>
#include <string>
#include <vector>

namespace Revolution {
	class Header_space {
	public:
		explicit Header_space(
			const std::string& exit = "EXIT",
			const std::string& get = "GET",
			const std::string& reset = "RESET",
			const std::string& response = "RESPONSE",
			const std::string& set = "SET",
			const std::string& status = "STATUS",
			const std::string& sync = "SYNC"
		);

		const std::string& get_exit() const;
		const std::string& get_get() const;
		const std::string& get_reset() const;
		const std::string& get_response() const;
		const std::string& get_set() const;
		const std::string& get_status() const;
		const std::string& get_sync() const;
	private:
		const std::string exit;
		const std::string get;
		const std::string reset;
		const std::string response;
		const std::string set;
		const std::string status;
		const std::string sync;
	};

	class Key_space {};

	class Topology {
	public:
		class Endpoint {
		public:
			explicit Endpoint(const std::string& name);

			const std::string& get_name() const;
		private:
			const std::string name;
		};

		explicit Topology(
			const Endpoint& marshal = Endpoint{"marshal"},
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

		const Endpoint& get_marshal() const;
		const Endpoint& get_display_driver() const;
		const Endpoint& get_miscellaneous_controller() const;
		const Endpoint& get_motor_controller() const;
		const Endpoint& get_power_sensor() const;
		const Endpoint& get_replica() const;
		const Endpoint& get_telemeter() const;
		const Endpoint& get_voltage_controller() const;

		const std::vector<std::reference_wrapper<const Endpoint>>
			get_soldiers() const;
	private:
		const Endpoint marshal;
		const Endpoint display_driver;
		const Endpoint miscellaneous_controller;
		const Endpoint motor_controller;
		const Endpoint power_sensor;
		const Endpoint replica;
		const Endpoint telemeter;
		const Endpoint voltage_controller;
	};
};

#endif  // REVOLUTION_CONFIGURATION_H
