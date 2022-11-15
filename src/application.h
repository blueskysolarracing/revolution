#ifndef REVOLUTION_APPLICATION_H
#define REVOLUTION_APPLICATION_H

#include <atomic>
#include <condition_variable>
#include <functional>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

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

		void main();
	protected:
		using Handler = std::function<
			std::vector<std::string>(const Messenger::Message&)
		>;

		const Header_space& get_header_space() const;
		const Key_space& get_key_space() const;
		const Topology& get_topology() const;
		const Logger& get_logger() const;
		const std::atomic_bool& get_status() const;

		std::optional<const std::reference_wrapper<const Handler>>
			get_handler(const std::string& header);
		void set_handler(
			const std::string& header,
			const Handler& handler
		);
		std::optional<std::string> get_state(const std::string& key);
		void set_state(
			const std::string& key,
			const std::string& value
		);
		virtual const Topology::Endpoint& get_endpoint() const = 0;
		virtual const Topology::Endpoint& get_syncer() const = 0;

		Messenger::Message send(
			const std::string& recipient_name,
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		) const;
		Messenger::Message communicate(
			const std::string& recipient_name,
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		);
		virtual void broadcast(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		) const = 0;
		virtual void broadcast(
			const Messenger::Message& message
		) const = 0;

		virtual void setup();
	private:
		const Messenger& get_messenger() const;
		const std::unordered_map<std::string, Handler>&
			get_handlers() const;
		const std::unordered_map<std::string, std::string>&
			get_states() const;
		const std::unordered_map<unsigned int, Messenger::Message>&
			get_responses() const;
		const std::mutex& get_handler_mutex() const;
		const std::mutex& get_state_mutex() const;
		const std::mutex& get_response_mutex() const;
		const std::condition_variable&
			get_response_condition_variable() const;

		std::atomic_bool& get_status();
		std::unordered_map<std::string, Handler>& get_handlers();
		std::unordered_map<std::string, std::string>& get_states();
		std::unordered_map<unsigned int, Messenger::Message>&
			get_responses();
		std::mutex& get_handler_mutex();
		std::mutex& get_state_mutex();
		std::mutex& get_response_mutex();
		std::condition_variable& get_response_condition_variable();

		Messenger::Message
			get_response(const Messenger::Message& message);
		void set_response(const Messenger::Message& message);

		std::vector<std::string>
			handle_exit(const Messenger::Message& message);
		std::vector<std::string>
			handle_read(const Messenger::Message& message);
		std::vector<std::string>
			handle_response(const Messenger::Message& message);
		std::vector<std::string>
			handle_status(const Messenger::Message& message) const;
		std::vector<std::string>
			handle_write(const Messenger::Message& message);
		void handle(const Messenger::Message& message);

		void run();

		const Header_space header_space;
		const Key_space key_space;
		const Topology topology;
		const Logger logger;
		const Messenger messenger;
		std::atomic_bool status;
		std::unordered_map<std::string, Handler> handlers;
		std::unordered_map<std::string, std::string> states;
		std::unordered_map<unsigned int, Messenger::Message> responses;
		std::mutex handler_mutex;
		std::mutex state_mutex;
		std::mutex response_mutex;
		std::condition_variable response_condition_variable;
	};
}

#endif	// REVOLUTION_APPLICATION_H
