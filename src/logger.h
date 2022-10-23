#ifndef REVOLUTION_LOGGER_H
#define REVOLUTION_LOGGER_H

#include <fstream>
#include <string>

namespace Revolution {
	class Logger : public std::ostream {
	public:
		struct Severity {
			static const Severity trace;
			static const Severity debug;
			static const Severity info;
			static const Severity warning;
			static const Severity error;
			static const Severity fatal;

			explicit Severity(const std::string& name, const unsigned int& level);

			const std::string name;
			const unsigned int level;
		};

		explicit Logger(const Severity& severity, const std::string& log_filename = "");
		~Logger();

		Logger& operator<<(const Severity& severity);
	private:
		const Severity& get_severity() const;
		std::ofstream& get_ofstream();

		void set_status(const bool& status);

		const Severity severity;
		std::ofstream ofstream;
	};
}

#endif  // REVOLUTION_LOGGER_H
