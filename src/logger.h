#ifndef REVOLUTION_LOGGER_H
#define REVOLUTION_LOGGER_H

#include <fstream>
#include <string>

namespace Revolution {
	class Logger : public std::ostream {
	public:
		struct Severity {
			explicit Severity(
				const std::string& name,
				const unsigned int& level
			);

			const std::string name;
			const unsigned int level;
		};

		struct Configuration {
			explicit Configuration(
				const Severity& severity,
				const std::string& filename = "",
				const std::ofstream::openmode& open_mode
					= std::ofstream::app
			);

			const Severity severity;
			const std::string filename;
			const std::ofstream::openmode open_mode;
		};

		static const Severity trace;
		static const Severity debug;
		static const Severity info;
		static const Severity warning;
		static const Severity error;
		static const Severity fatal;

		explicit Logger(
			const Configuration& configuration
		);
		~Logger();

		Logger& operator<<(const Severity& severity);
	private:
		const Configuration& get_configuration() const;
		std::ofstream& get_ofstream();

		void set_status(const bool& status);

		const Configuration configuration;
		std::ofstream ofstream;
	};
}

#endif  // REVOLUTION_LOGGER_H
