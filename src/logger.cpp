#include <chrono>
#include <iomanip>
#include <iostream>

#include "logger.h"

namespace Revolution {
	const Logger::Severity Logger::Severity::trace{"trace", 0};
	const Logger::Severity Logger::Severity::debug{"debug", 1};
	const Logger::Severity Logger::Severity::info{"info", 2};
	const Logger::Severity Logger::Severity::warning{"warning", 3};
	const Logger::Severity Logger::Severity::error{"error", 4};
	const Logger::Severity Logger::Severity::fatal{"fatal", 5};

	Logger::Severity::Severity(const std::string& name, const unsigned int& level)
		: name{name}, level{level}
	{
	}

	Logger::Logger(const Severity& severity, const std::string& log_filename)
		: std::ostream{nullptr}, severity{severity}, ofstream{}
	{
		if (!log_filename.empty())
			get_ofstream().open(log_filename, std::ofstream::app);

		set_status(true);

		if (get_ofstream().fail()) {
			(*this) << Severity::error << "Cannot open log file. Using stdout instead." << std::endl;
			get_ofstream().clear();
		}
	}

	Logger::~Logger()
	{
		if (get_ofstream().is_open())
			get_ofstream().close();

		if (get_ofstream().fail()) {
			(*this) << Severity::error << "Cannot close log file." << std::endl;
			get_ofstream().clear();
		}
	}

	Logger& Logger::operator<<(const Severity& severity)
	{
		set_status(severity.level >= get_severity().level);

		auto time_point = std::chrono::system_clock::now();
		auto time = std::chrono::system_clock::to_time_t(time_point);

		(*this) << '[' << std::put_time(std::localtime(&time), "%c")
			<< "] [" << severity.name << "]: ";

		return *this;
	}

	const Logger::Severity& Logger::get_severity() const
	{
		return severity;
	}

	std::ofstream& Logger::get_ofstream()
	{
		return ofstream;
	}

	void Logger::set_status(const bool& status)
	{
		if (!status)
			rdbuf(nullptr);
		else if (get_ofstream().is_open())
			rdbuf(get_ofstream().rdbuf());
		else
			rdbuf(std::cout.rdbuf());
	}
}
