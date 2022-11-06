#include <iostream>
#include <mutex>
#include <sstream>

#include "logger.h"

namespace Revolution {
	Logger::Severity::Severity(const unsigned int& level) : level{level}
	{
	}

	const unsigned int& Logger::Severity::get_level() const
	{
		return level;
	}

	Logger::Log_stream::Log_stream(const Severity& severity)
		: std::ostringstream{}, severity{severity}
	{
	}

	Logger::Log_stream::~Log_stream()
	{
		std::scoped_lock lock(get_mutex());

		std::cout << '<' << get_severity().get_level() << '>' << str();
		std::cout.flush();
	}

	const Logger::Severity& Logger::Log_stream::get_severity() const
	{
		return severity;
	}

	std::mutex Logger::Log_stream::mutex{};

	std::mutex& Logger::Log_stream::get_mutex()
	{
		return mutex;
	}

	Logger::Configuration::Configuration()
	{
	}

	const Logger::Severity Logger::emergency{0};
	const Logger::Severity Logger::alert{1};
	const Logger::Severity Logger::critical{2};
	const Logger::Severity Logger::error{3};
	const Logger::Severity Logger::warning{4};
	const Logger::Severity Logger::notice{5};
	const Logger::Severity Logger::information{6};
	const Logger::Severity Logger::debug{7};

	Logger::Logger(
		const Configuration& configuration
	) : configuration{configuration}
	{
	}

	Logger::Log_stream Logger::operator<<(const Severity& severity) const
	{
		return Log_stream{severity};
	}

	const Logger::Configuration& Logger::get_configuration() const
	{
		return configuration;
	}
}
