#include "logger.h"

#include <iostream>
#include <mutex>
#include <sstream>

#include <syslog.h>

namespace Revolution {
    Logger::LogStream::LogStream(const Severity& severity)
            : severity{severity} {}

    Logger::LogStream::~LogStream() {
        int priority;

        switch (get_severity()) {
            case Severity::emergency:
                priority = LOG_EMERG;
                break;
            case Severity::alert:
                priority = LOG_ALERT;
                break;
            case Severity::critical:
                priority = LOG_CRIT;
                break;
            case Severity::error:
                priority = LOG_ERR;
                break;
            case Severity::warning:
                priority = LOG_WARNING;
                break;
            case Severity::notice:
                priority = LOG_NOTICE;
                break;
            case Severity::information:
                priority = LOG_INFO;
                break;
            case Severity::debug:
                priority = LOG_DEBUG;
                break;
            default:
                priority = -1;
                break;
        }

        std::scoped_lock lock{get_mutex()};

        std::cout << '<' << priority << '>' << str() << std::endl;
    }

    const Logger::Severity& Logger::LogStream::get_severity() const {
        return severity;
    }

    std::mutex Logger::LogStream::mutex{};

    std::mutex& Logger::LogStream::get_mutex() {
        return mutex;
    }

    Logger::LogStream Logger::operator<<(const Severity& severity) const {
        return LogStream{severity};
    }
}
