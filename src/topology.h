#ifndef REVOLUTION_TOPOLOGY_H
#define REVOLUTION_TOPOLOGY_H

#include <sys/stat.h>

#include "logger.h"

namespace Revolution {
	struct Configuration {
		struct Applications {
			struct Parameters {
				explicit Parameters(
					const Logger::Severity& logger_severity,
					const std::string& logger_filename,
					const std::ofstream::openmode& logger_open_mode,
					const std::string& messenger_name,
					const int& messenger_oflags,
					const mode_t& messenger_mode,
					const unsigned int& messenger_priority,
					const bool& messenger_unlink_status,
					const std::string& name,
					const std::string& pid_filename,
					const std::string& binary_filename
				);

				const Logger::Severity logger_severity;
				const std::string logger_filename;
				const std::ofstream::openmode logger_open_mode;

				const std::string messenger_name;
				const int messenger_oflags;
				const mode_t messenger_mode;
				const unsigned int messenger_priority;
				const bool messenger_unlink_status;

				const std::string name;
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
