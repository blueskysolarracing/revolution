#include "logger.h"

#include <iostream>

namespace Revolution {
    Logger::LogStream::LogStream(const Severity& severity) :
            severity{severity} {}

    Logger::LogStream::~LogStream() {
        std::scoped_lock lock{get_mutex()};

        std::cout << '<' << static_cast<int>(get_severity()) << '>' << str();
    }

    const Logger::Severity& Logger::LogStream::get_severity() const {
        return severity;
    }

    std::mutex& Logger::LogStream::get_mutex() {
        return mutex;
    }

    std::mutex Logger::LogStream::mutex{};

    Logger::LogStream Logger::operator<<(const Severity& severity) const {
        return LogStream{severity};
    }
}
