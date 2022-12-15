#ifndef REVOLUTION_LOGGER_H
#define REVOLUTION_LOGGER_H

#include <mutex>
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
            static std::mutex mutex;

            static std::mutex& get_mutex();

            const Severity severity;
        };

        explicit Logger() = default;

        LogStream operator<<(const Severity& severity) const;
    };
}

#endif  // REVOLUTION_LOGGER_H
