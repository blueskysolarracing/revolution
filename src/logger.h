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

		class Log_stream : public std::ostringstream {
		public:
			explicit Log_stream(const Severity& severity);
			~Log_stream();

			const Severity& get_severity() const;
		private:
			static std::mutex mutex;

			static std::mutex& get_mutex();

			const Severity severity;
		};

		Log_stream operator<<(const Severity& severity) const;
	};
}

#endif  // REVOLUTION_LOGGER_H
