#ifndef REVOLUTION_LOGGER_H
#define REVOLUTION_LOGGER_H

#include <sstream>

namespace Revolution {
    class Logger {
    public:
        enum class Severity {
            emergency,
            alert,
            critical,
            error,
            warning,
            notice,
            information,
            debug
        };

        class LogStream : public std::ostringstream {
        public:
            explicit LogStream(const Severity& severity);
            ~LogStream();

            const Severity& get_severity() const;
        private:
            const Severity severity;
        };

        explicit Logger() = default;

        LogStream operator<<(const Severity& severity) const;
    };
}

#endif  // REVOLUTION_LOGGER_H
