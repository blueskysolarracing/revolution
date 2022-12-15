#include "logger.h"

#include <sstream>

#include <systemd/sd-journal.h>

namespace Revolution {
    Logger::LogStream::LogStream(const Severity& severity)
            : severity{severity} {}

    Logger::LogStream::~LogStream() {
        sd_journal_print(static_cast<int>(get_severity()), str().data());
    }

    const Logger::Severity& Logger::LogStream::get_severity() const {
        return severity;
    }

    Logger::LogStream Logger::operator<<(const Severity& severity) const {
        return LogStream{severity};
    }
}
