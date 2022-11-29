#include "logger.h"

#include <sstream>

#include <systemd/sd-journal.h>

namespace Revolution {
	Logger::Log_stream::Log_stream(const Severity& severity)
		: std::ostringstream{}, severity{severity} {}

	Logger::Log_stream::~Log_stream() {
		sd_journal_print(
			static_cast<int>(get_severity()),
			str().data()
		);
	}

	const Logger::Severity& Logger::Log_stream::get_severity() const {
		return severity;
	}

	Logger::Log_stream Logger::operator<<(const Severity& severity) const {
		return Log_stream{severity};
	}
}
