#include <chrono>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <sstream>
#include <string>

#include "logger.h"

namespace Revolution {
	Logger::Severity::Severity(
		const std::string& name,
		const unsigned int& level
	) : name{name}, level{level}
	{
	}

	Logger::Configuration::Configuration(const Severity& severity)
		: severity{severity}
	{
	}

	Logger::Log_stream::Log_stream(const Severity& severity)
		: std::ostringstream{}
	{
		auto time_point = std::chrono::system_clock::now();
		auto time = std::chrono::system_clock::to_time_t(time_point);

		(*this) << '['
			<< std::put_time(std::localtime(&time), "%c")
			<< "] ["
			<< severity.name
			<< "]: ";

	}

	Logger::Log_stream::~Log_stream()
	{
		std::scoped_lock lock(get_mutex());

		std::cout << str();
		std::cout.flush();
	}

	std::mutex Logger::Log_stream::mutex{};

	std::mutex& Logger::Log_stream::get_mutex()
	{
		return mutex;
	}

	const Logger::Severity Logger::trace{"trace", 0};
	const Logger::Severity Logger::debug{"debug", 1};
	const Logger::Severity Logger::info{"info", 2};
	const Logger::Severity Logger::warning{"warning", 3};
	const Logger::Severity Logger::error{"error", 4};
	const Logger::Severity Logger::fatal{"fatal", 5};

	Logger::Logger(
		const Configuration& configuration
	) : configuration{configuration}
	{
	}

	const Logger::Log_stream Logger::operator<<(const Severity& severity)
	{
		return Log_stream{severity};
	}

	const Logger::Configuration& Logger::get_configuration() const
	{
		return configuration;
	}

	bool Logger::get_status(const Severity& severity) const
	{
		return severity.level >= get_configuration().severity.level;
	}
}
