#ifndef REVOLUTION_LOGGER_H
#define REVOLUTION_LOGGER_H

#include <mutex>
#include <sstream>

namespace Revolution {
	class Logger {
	public:
		class Configuration {
		public:
			explicit Configuration(const bool& status);

			const bool& get_status() const;
		private:
			const bool status;
		};

		class Severity {
		public:
			explicit Severity(const unsigned int& level);

			const unsigned int& get_level() const;
		private:
			const unsigned int level;
		};

		class Log_stream : public std::ostringstream {
		public:
			explicit Log_stream(
				const Configuration& configuration,
				const Severity& severity
			);
			~Log_stream();

			const Configuration& get_configuration() const;
			const Severity& get_severity() const;
		private:
			static std::mutex mutex;

			static std::mutex& get_mutex();

			const Configuration& configuration;
			const Severity& severity;
		};

		static const Severity emergency;
		static const Severity alert;
		static const Severity critical;
		static const Severity error;
		static const Severity warning;
		static const Severity notice;
		static const Severity information;
		static const Severity debug;

		explicit Logger(const Configuration& configuration);

		Log_stream operator<<(const Severity& severity) const;

		const Configuration& get_configuration() const;
	private:
		const Configuration configuration;
	};
}

#endif  // REVOLUTION_LOGGER_H
