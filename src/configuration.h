#ifndef REVOLUTION_TOPOLOGY_H
#define REVOLUTION_TOPOLOGY_H

#include "logger.h"

namespace Revolution {
	struct Configuration {
		struct Applications {
			struct Parameters {
				explicit Parameters(
					const std::string& name,
					const unsigned int& priority,
					const Logger::Severity& log_severity,
					const std::string& log_filename,
					const std::ofstream::openmode& log_open_mode,
					const std::string& pid_filename,
					const std::string& binary_filename
				);

				const std::string name;
				const unsigned int priority;
				const Logger::Severity log_severity;
				const std::string log_filename;
				const std::ofstream::openmode log_open_mode;
				const std::string pid_filename;
				const std::string binary_filename;
			};

			Applications(
				const Parameters& syncer,
				const Parameters& display_driver,
				const Parameters& miscellaneous_controller,
				const Parameters& motor_controller,
				const Parameters& power_sensor,
				const Parameters& telemeter,
				const Parameters& voltage_controller
			);

			const Parameters syncer;
			const Parameters display_driver;
			const Parameters miscellaneous_controller;
			const Parameters motor_controller;
			const Parameters power_sensor;
			const Parameters telemeter;
			const Parameters voltage_controller;
		};

		struct Headers {
			explicit Headers(
				const std::string& get_command,
				const std::string& set_command,
				const std::string& exit_command,
				const std::string& state_broadcast
			);

			const std::string get_command;
			const std::string set_command;
			const std::string exit_command;

			const std::string state_broadcast;
		};

		Configuration();

		const Applications applications;
		const Headers headers;
	};
};

#endif  // REVOLUTION_TOPOLOGY_H
