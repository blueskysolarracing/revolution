#ifndef REVOLUTION_LOGGER_H
#define REVOLUTION_LOGGER_H

#include <mutex>
#include <sstream>

namespace Revolution {
	class Logger {
	public:
		class Severity {
		public:
			explicit Severity(const unsigned int& level);

			const unsigned int& get_level() const;
		private:
			const unsigned int level;
		};

		class Log_stream : public std::ostringstream {
		public:
			explicit Log_stream(const Severity& severity);
			~Log_stream();

			const Severity& get_severity() const;
		private:
			static std::mutex mutex;

			static std::mutex& get_mutex();

			const Severity& severity;
		};

		class Configuration {
		public:
			explicit Configuration();
		};

		static const Logger::Severity emergency;
		static const Logger::Severity alert;
		static const Logger::Severity critical;
		static const Logger::Severity error;
		static const Logger::Severity warning;
		static const Logger::Severity notice;
		static const Logger::Severity information;
		static const Logger::Severity debug;

		explicit Logger(
			const Configuration& configuration
		);

		Log_stream operator<<(const Severity& severity) const;
	private:
		const Configuration& get_configuration() const;

		const Configuration configuration;
	};
}

#endif  // REVOLUTION_LOGGER_H
