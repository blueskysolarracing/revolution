#ifndef REVOLUTION_LOGGER_H
#define REVOLUTION_LOGGER_H

#include <fstream>
#include <string>

namespace Revolution {
	class Log_level {
	public:
		static const Log_level trace;
		static const Log_level debug;
		static const Log_level info;
		static const Log_level warning;
		static const Log_level error;
		static const Log_level fatal;

		const std::string &get_name() const;
		const unsigned int &get_severity() const;
	private:
		explicit Log_level(const std::string &name, const unsigned int &severity);

		const std::string name;
		const unsigned int severity;
	};

	class Logger {
	public:
		Logger(const Log_level &log_level, const std::string &log_filename = "");
		~Logger();

		const Log_level &get_log_level() const;

		void log(const Log_level& log_level, const std::string &string);
	private:
		std::ostream &get_ostream();

		const Log_level log_level;
		std::fstream fstream;
	};
}

#endif  // REVOLUTION_LOGGER_H
