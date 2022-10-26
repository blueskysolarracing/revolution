#ifndef REVOLUTION_TOPOLOGY_H
#define REVOLUTION_TOPOLOGY_H

#include "application.h"

namespace Revolution {
	struct Topology {
		struct Endpoint {
			explicit Endpoint(
				const std::string& name,
				const Logger::Configuration& logger_configuration,
				const Messenger::Configuration& messenger_configuration,
				const std::string& binary_filename
			);

			const std::string name;
			const Logger::Configuration logger_configuration;
			const Messenger::Configuration messenger_configuration;
			const std::string binary_filename;

			std::string get_command() const;
		};

		explicit Topology(
			const Endpoint& syncer = Endpoint{
				"syncer",
				Logger::Configuration{
					Logger::info,
					"./syncer.log"
				},
				Messenger::Configuration{
					"/revolution_syncer",
					true
				},
				"./syncer"
			},
			const Endpoint& display_driver = Endpoint{
				"display_driver",
				Logger::Configuration{
					Logger::info,
					"./display_driver.log"
				},
				Messenger::Configuration{
					"/revolution_display_driver"
				},
				"./display_driver"
			},
			const Endpoint& miscellaneous_controller = Endpoint{
				"miscellaneous_controller",
				Logger::Configuration{
					Logger::info,
					"./miscellaneous_controller.log"
				},
				Messenger::Configuration{
					"/revolution_miscellaneous_controller"
				},
				"./miscellaneous_controller"
			},
			const Endpoint& motor_controller = Endpoint{
				"motor_controller",
				Logger::Configuration{
					Logger::info,
					"./motor_controller.log"
				},
				Messenger::Configuration{
					"/revolution_motor_controller"
				},
				"./motor_controller"
			},
			const Endpoint& power_sensor = Endpoint{
				"power_sensor",
				Logger::Configuration{
					Logger::info,
					"./power_sensor.log"
				},
				Messenger::Configuration{
					"/revolution_power_sensor"
				},
				"./power_sensor"
			},
			const Endpoint& telemeter = Endpoint{
				"telemeter",
				Logger::Configuration{
					Logger::info,
					"./telemeter.log"
				},
				Messenger::Configuration{
					"/revolution_telemeter"
				},
				"./telemeter"
			},
			const Endpoint& voltage_controller = Endpoint{
				"voltage_controller",
				Logger::Configuration{
					Logger::info,
					"./voltage_controller.log"
				},
				Messenger::Configuration{
					"/revolution_voltage_controller"
				},
				"./voltage_controller"
			},
			const Endpoint& watchdog = Endpoint{
				"watchdog",
				Logger::Configuration{
					Logger::info,
					"./watchdog.log"
				},
				Messenger::Configuration{
					"/revolution_watchdog"
				},
				"./watchdog"
			}
		);

		const Endpoint& get_master() const;
		const std::vector<Endpoint> get_slaves() const;
		const std::vector<Endpoint> get_endpoints() const;

		const Endpoint syncer;
		const Endpoint display_driver;
		const Endpoint miscellaneous_controller;
		const Endpoint motor_controller;
		const Endpoint power_sensor;
		const Endpoint telemeter;
		const Endpoint voltage_controller;
		const Endpoint watchdog;
	};

	struct Header_space {
		explicit Header_space(
			const std::string& status = "STATUS",
			const std::string& get = "GET",
			const std::string& set = "SET",
			const std::string& reset = "RESET",
			const std::string& sync = "SYNC",
			const std::string& exit = "EXIT",
			const std::string& response = "RESPONSE"
		);

		const std::string status;
		const std::string get;
		const std::string set;
		const std::string reset;
		const std::string sync;
		const std::string exit;
		const std::string response;
	};

	struct Key_space {
		explicit Key_space(
			const std::string& heartbeat_suffix = "_HEARTBEAT"
		);

		std::string get_heartbeat(const std::string& name) const;

		const std::string heartbeat_suffix;
	};
};

#endif  // REVOLUTION_TOPOLOGY_H
