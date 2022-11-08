#ifndef REVOLUTION_APPLICATION_H
#define REVOLUTION_APPLICATION_H

#include <functional>
#include <string>
#include <unordered_map>

#include "configuration.h"
#include "logger.h"
#include "messenger.h"

namespace Revolution {
	class Application {
	public:
		explicit Application(
			const Header_space& header_space,
			const Key_space& key_space,
			const Topology& topology
		);

		virtual void run();
	protected:
		using Handler = std::function<void(const Messenger::Message&)>;
		using Handlers = std::unordered_map<std::string, Handler>;
		using States = std::unordered_map<std::string, std::string>;

		const Topology& get_topology() const;
		const Header_space& get_header_space() const;
		const Key_space& get_key_space() const;
		const Logger& get_logger() const;
		const Messenger& get_messenger() const;
		Heart& get_heart() const;
		const bool& get_status() const;
		void set_status(const bool& status);
		const States& get_states() const;
		std::vector<std::string> get_state_data() const;
		void set_handler(
			const std::string& name,
			const Handler& handler
		);
		virtual const Topology::Endpoint& get_endpoint() const = 0;

		void handle_exit(const Messenger::Message& message);
		void handle_read(const Messenger::Message& message) const;
		void handle_status(const Messenger::Message& message) const;
		void handle_sync(const Messenger::Message& message) const;
		virtual void handle_write(const Messenger::Message& message);
	private:
		const Handlers& get_handlers() const;
		Handlers& get_handlers();
		States& get_states();

		void handle(const Messenger::Message& message) const;

		const Header_space& header_space;
		const Key_space& key_space;
		const Topology& topology;
		const Logger& logger;
		const Messenger& messenger;
		std::atomic_bool status;
		Handlers handlers;
		States states;
	};
}

#endif	// REVOLUTION_APPLICATION_H
