#ifndef REVOLUTION_LOGGER_H
#define REVOLUTION_LOGGER_H

#include <mutex>
#include <sstream>
#include <string>

namespace Revolution {
	class Logger {
	public:
		struct Severity {
			explicit Severity(
				const std::string& name,
				const unsigned int& level
			);

			const std::string name;
			const unsigned int level;
		};

		struct Configuration {
			explicit Configuration(
				const Severity& severity
			);

			const Severity severity;
		};

		class Log_stream : public std::ostringstream {
		public:
			explicit Log_stream(const Severity& severity);
			~Log_stream();
		private:
			static std::mutex mutex;

			static std::mutex& get_mutex();
		};

		static const Severity trace;
		static const Severity debug;
		static const Severity info;
		static const Severity warning;
		static const Severity error;
		static const Severity fatal;

		explicit Logger(
			const Configuration& configuration
		);

		const Log_stream operator<<(const Severity& severity);
	private:
		const Configuration& get_configuration() const;
		bool get_status(const Severity& severity) const;

		const Configuration configuration;
	};
}

#endif  // REVOLUTION_LOGGER_H
