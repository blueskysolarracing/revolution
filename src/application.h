#ifndef REVOLUTION_APPLICATION_H
#define REVOLUTION_APPLICATION_H

#include "messenger.h"

namespace Revolution {
	class Application {
	public:
		explicit Application(
			const std::string& name,
			const Logger::Configuration& logger_configuration,
			const Messenger::Configuration& messenger_configuration
		);
		~Application();

		virtual void run();
	protected:
		const std::string& get_name() const;
		Logger& get_logger();
		Messenger& get_messenger();
		const bool& get_status() const;
		void set_status(const bool& status);
		void set_handler(const std::string& name, std::function<void(const Messenger::Message&)> handler);

		virtual void update(
			const std::optional<Messenger::Message>& optional_message
		);
	private:
		const std::unordered_map<std::string, std::function<void(const Messenger::Message&)>>& get_handlers() const;
		std::unordered_map<std::string, std::function<void(const Messenger::Message&)>>& get_handlers();
		std::optional<std::function<void(const Messenger::Message&)>> get_handler(const std::string& name) const;

		void handle(const Messenger::Message& message);

		const std::string name;
		Logger logger;
		Messenger messenger;
		std::unordered_map<std::string, std::function<void(const Messenger::Message&)>> handlers;
		bool status;
	};
}

#endif	// REVOLUTION_APPLICATION_H
