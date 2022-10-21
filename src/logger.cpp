#include <chrono>
#include <iomanip>
#include <iostream>

#include "logger.h"

namespace Revolution {
	const Log_level Log_level::trace("trace", 0);
	const Log_level Log_level::debug("debug", 1);
	const Log_level Log_level::info("info", 2);
	const Log_level Log_level::warning("warning", 3);
	const Log_level Log_level::error("error", 4);
	const Log_level Log_level::fatal("fatal", 5);

	const std::string &Log_level::get_name() const
	{
		return name;
	}

	const unsigned int &Log_level::get_severity() const
	{
		return severity;
	}

	Log_level::Log_level(const std::string &name, const unsigned int &severity)
		: name{name}, severity{severity}
	{
	}

	Logger::Logger(const Log_level &log_level, const std::string &log_filename)
		: log_level{log_level}, fstream{}
	{
		if (!log_filename.empty()) {
			fstream.open(log_filename, std::fstream::out);

			if (fstream.fail()) {
				log(Log_level::error, "Cannot open log file. Using stdout instead.");
			}
		}
	}

	Logger::~Logger()
	{
		if (fstream.is_open()) {
			fstream.close();

			if (fstream.fail()) {
				log(Log_level::error, "Cannot close log file.");
			}
		}
	}

	const Log_level &Logger::get_log_level() const
	{
		return log_level;
	}

	void Logger::log(const Log_level& log_level, const std::string &string)
	{
		if (log_level.get_severity() < get_log_level().get_severity())
			return;

		auto time_point = std::chrono::system_clock::now();
		auto time = std::chrono::system_clock::to_time_t(time_point);

		get_ostream() << '[' << std::put_time(std::localtime(&time), "%c")
			<< "] [" << log_level.get_name()
			<< "]: " << string << std::endl;
	}

	std::ostream &Logger::get_ostream()
	{
		if (fstream.is_open())
			return fstream;
		else
			return std::cout;
	}
}
