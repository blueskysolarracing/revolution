#ifndef REVOLUTION_LOGGER_H
#define REVOLUTION_LOGGER_H

#include <mutex>
#include <sstream>

#include <syslog.h>

namespace Revolution {
    class Logger {
    public:
        enum class Severity {
            emergency = LOG_EMERG,
            alert = LOG_ALERT,
            critical = LOG_CRIT,
            error = LOG_ERR,
            warning = LOG_WARNING,
            notice = LOG_NOTICE,
            information = LOG_INFO,
            debug = LOG_DEBUG
        };

        class LogStream : public std::ostringstream {
        public:
            explicit LogStream(const Severity& severity);
            ~LogStream();

            const Severity& get_severity() const;
        private:
            static std::mutex& get_mutex();

            static std::mutex mutex;

            const Severity severity;
        };

        explicit Logger() = default;

        LogStream operator<<(const Severity& severity) const;
    };
}

#endif  // REVOLUTION_LOGGER_H
