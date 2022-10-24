#ifndef REVOLUTION_APPLICATION_H
#define REVOLUTION_APPLICATION_H

#include "messenger.h"

namespace Revolution {
	class Application {
	public:
		struct Configuration {
			explicit Configuration(
				const std::string& name,
				const Logger::Configuration& logger_configuration,
				const Messenger::Configuration& messenger_configuration
			);

			const std::string name;
			const Logger::Configuration logger_configuration;
			const Messenger::Configuration messenger_configuration;
		};

		explicit Application(const Configuration& configuration);
		~Application();

		virtual void run();
	protected:
		const Configuration& get_configuration() const;
		Logger& get_logger();
		Messenger& get_messenger();
		const bool& get_status() const;
		void set_status(const bool& status);
		void set_handler(const std::string& name, std::function<void(const std::vector<std::string>&)> handler);
	private:
		const std::unordered_map<std::string, std::function<void(const std::vector<std::string>&)>>& get_handlers() const;
		std::unordered_map<std::string, std::function<void(const std::vector<std::string>&)>>& get_handlers();
		std::optional<std::function<void(const std::vector<std::string>&)>> get_handler(const std::string& name) const;

		void handle(const Messenger::Message& message);

		Configuration configuration;
		Logger logger;
		Messenger messenger;
		std::unordered_map<std::string, std::function<void(const std::vector<std::string>&)>> handlers;
		bool status;
	};
}

#endif	// REVOLUTION_APPLICATION_H
