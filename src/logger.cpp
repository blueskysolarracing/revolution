#include "logger.h"

#include <iostream>
#include <mutex>
#include <sstream>

namespace Revolution {
	Logger::Log_stream::Log_stream(const Severity& severity)
		: std::ostringstream{}, severity{severity} {}

	Logger::Log_stream::~Log_stream() {
		std::scoped_lock lock{get_mutex()};

		std::cout << '<'
			<< static_cast<int>(get_severity())
			<< '>'
			<< str()
			<< std::flush;
	}

	const Logger::Severity& Logger::Log_stream::get_severity() const {
		return severity;
	}

	std::mutex Logger::Log_stream::mutex{};

	std::mutex& Logger::Log_stream::get_mutex() {
		return mutex;
	}

	Logger::Log_stream Logger::operator<<(const Severity& severity) const {
		return Log_stream{severity};
	}
}
