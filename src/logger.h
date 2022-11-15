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

		class Log_stream : public std::ostringstream {
		public:
			explicit Log_stream(const Severity& severity);
			~Log_stream();

			const Severity& get_severity() const;
		private:
			const Severity severity;
		};

		Log_stream operator<<(const Severity& severity) const;
	};
}

#endif  // REVOLUTION_LOGGER_H
