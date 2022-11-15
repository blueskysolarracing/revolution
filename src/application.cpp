#include "application.h"

#include <atomic>
#include <condition_variable>
#include <cstddef>
#include <functional>
#include <list>
#include <mutex>
#include <optional>
#include <ostream>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>

#include "configuration.h"
#include "logger.h"
#include "messenger.h"
#include "worker_pool.h"

namespace Revolution {
	Application::Application(
		const Header_space& header_space,
		const Key_space& key_space,
		const Topology& topology
	) : header_space{header_space},
	    key_space{key_space},
	    topology{topology},
	    logger{},
	    messenger{},
	    status{},
	    handlers{},
	    states{},
	    responses{},
	    handler_mutex{},
	    state_mutex{},
	    response_mutex{},
	    response_condition_variable{} {}

	void Application::main() {
		get_logger() << Logger::Severity::information
			<< "Starting: \""
			<< get_endpoint().get_name()
			<< "\"..."
			<< std::endl;

		setup();
		run();

		get_logger() << Logger::Severity::information
			<< "Stopping: \""
			<< get_endpoint().get_name()
			<< "\"..."
			<< std::endl;
	}

	const Header_space& Application::get_header_space() const {
		return header_space;
	}

	const Key_space& Application::get_key_space() const {
		return key_space;
	}

	const Topology& Application::get_topology() const {
		return topology;
	}

	const Logger& Application::get_logger() const {
		return logger;
	}

	const std::atomic_bool& Application::get_status() const {
		return status;
	}

	std::optional<const std::reference_wrapper<const Application::Handler>>
		Application::get_handler(const std::string& header) {
		std::scoped_lock lock{get_handler_mutex()};

		if (!get_handlers().count(header))
			return std::nullopt;

		return get_handlers().at(header);
	}

	void Application::set_handler(
		const std::string& header,
		const Handler& handler
	) {
		std::scoped_lock lock{get_handler_mutex()};

		if (get_handlers().count(header))
			get_logger() << Logger::Severity::warning
				<< "Overriding an existing handler: \""
				<< header
				<< "\"..."
				<< std::endl;
		else
			get_logger() << Logger::Severity::information
				<< "Adding handler: \""
				<< header
				<< "\"..."
				<< std::endl;

		get_handlers().emplace(header, handler);
	}

	std::optional<std::string>
		Application::get_state(const std::string& key) {
		std::scoped_lock lock{get_state_mutex()};

		if (!get_states().count(key)) {
			get_logger() << Logger::Severity::warning
				<< "Key \""
				<< key
				<< "\" not found. "
				<< "Using std::nullopt."
				<< std::endl;

			return std::nullopt;
		}

		return get_states().at(key);
	}

	void Application::set_state(
		const std::string& key,
		const std::string& value
	) {
		std::scoped_lock lock{get_state_mutex()};

		get_states().emplace(key, value);

		broadcast(get_header_space().get_set(), {key, value});
	}

	Messenger::Message Application::send(
		const std::string& recipient_name,
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) const {
		Messenger::Message message{
			get_endpoint().get_name(),
			recipient_name,
			header,
			data,
			priority
		};

		get_messenger().send(message);

		return message;
	}

	Messenger::Message Application::communicate(
		const std::string& recipient_name,
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) {
		auto message = send(recipient_name, header, data, priority);

		return get_response(message);
	}

	void Application::setup() {
		get_status() = true;

		get_logger() << Logger::Severity::information
			<< "Adding handlers..."
			<< std::endl;

		set_handler(
			get_header_space().get_exit(),
			std::bind(
				&Application::handle_exit,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_get(),
			std::bind(
				&Application::handle_read,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_reset(),
			std::bind(
				&Application::handle_write,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_response(),
			std::bind(
				&Application::handle_response,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_set(),
			std::bind(
				&Application::handle_write,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_status(),
			std::bind(
				&Application::handle_status,
				this,
				std::placeholders::_1
			)
		);

		get_logger() << Logger::Severity::information
			<< "Syncing with "
			<< get_syncer().get_name()
			<< "..."
			<< std::endl;

		auto message = communicate(
			get_syncer().get_name(),
			get_header_space().get_get()
		);

		handle_write(
			Messenger::Message{
				message.get_sender_name(),
				message.get_recipient_name(),
				get_header_space().get_reset(),
				message.get_data(),
				message.get_priority(),
				message.get_identity()
			}
		);
	}

	const Messenger& Application::get_messenger() const {
		return messenger;
	}

	const std::unordered_map<std::string, Application::Handler>&
		Application::get_handlers() const {
		return handlers;
	}

	const std::unordered_map<std::string, std::string>&
		Application::get_states() const {
		return states;
	}

	const std::unordered_map<unsigned int, Messenger::Message>&
		Application::get_responses() const {
		return responses;
	}

	const std::mutex& Application::get_handler_mutex() const {
		return handler_mutex;
	}

	const std::mutex& Application::get_state_mutex() const {
		return state_mutex;
	}

	const std::mutex& Application::get_response_mutex() const {
		return response_mutex;
	}

	const std::condition_variable&
		Application::get_response_condition_variable() const {
		return response_condition_variable;
	}

	std::atomic_bool& Application::get_status() {
		return status;
	}

	std::unordered_map<std::string, Application::Handler>&
		Application::get_handlers() {
		return handlers;
	}

	std::unordered_map<std::string, std::string>&
		Application::get_states() {
		return states;
	}

	std::unordered_map<unsigned int, Messenger::Message>&
		Application::get_responses() {
		return responses;
	}

	std::mutex& Application::get_handler_mutex() {
		return handler_mutex;
	}

	std::mutex& Application::get_state_mutex() {
		return state_mutex;
	}

	std::mutex& Application::get_response_mutex() {
		return response_mutex;
	}

	std::condition_variable& Application::get_response_condition_variable() {
		return response_condition_variable;
	}

	Messenger::Message
		Application::get_response(const Messenger::Message& message) {
		std::unique_lock lock{get_response_mutex()};

		while (!get_responses().count(message.get_identity()))
			get_response_condition_variable().wait(lock);

		auto response = get_responses().at(message.get_identity());

		get_responses().erase(message.get_identity());

		return response;
	}

	void Application::set_response(const Messenger::Message& message) {
		std::unique_lock lock{get_response_mutex()};

		get_responses().emplace(message.get_identity(), message);

		lock.unlock();
		get_response_condition_variable().notify_all();
	}

	std::vector<std::string>
		Application::handle_exit(const Messenger::Message& message) {
		if (!message.get_data().empty())
			get_logger() << Logger::Severity::warning
				<< "Exit expects no arguments, "
				<< "but at least one was supplied. "
				<< "They will be ignored."
				<< std::endl;

		get_logger() << Logger::Severity::information
			<< "Exiting gracefully..."
			<< std::endl;

		get_status() = false;

		return {};
	}

	std::vector<std::string> Application::handle_read(
		const Messenger::Message& message
	) {
		std::scoped_lock lock{get_state_mutex()};
		std::vector<std::string> data;

		if (message.get_data().empty()) {
			get_logger() << Logger::Severity::information
				<< "Reading all key(s)..."
				<< std::endl;

			for (const auto& [key, value] : get_states()) {
				data.push_back(key);
				data.push_back(value);
			}
		} else {
			get_logger() << Logger::Severity::information
				<< "Reading "
				<< message.get_data().size()
				<< " key(s)..."
				<< std::endl;

			for (const auto& key : message.get_data()) {
				data.push_back(key);

				if (get_states().count(key))
					data.push_back(get_states().at(key));
				else
					get_logger()
						<< Logger::Severity::warning
						<< "Key \""
						<< key
						<< "\" not found. "
						<< "Ignoring key..."
						<< std::endl;
			}
		}

		return data;
	}

	std::vector<std::string> Application::handle_response(
		const Messenger::Message& message
	) {
		set_response(message);

		return {};
	}

	std::vector<std::string> Application::handle_status(
		const Messenger::Message& message
	) const {
		if (!message.get_data().empty())
			get_logger() << Logger::Severity::warning
				<< "Status expects no arguments, "
				<< "but at least one was supplied. "
				<< "They will be ignored."
				<< std::endl;

		get_logger() << Logger::Severity::information
			<< "Status report requested. Sending response..."
			<< std::endl;

		return {};
	}

	std::vector<std::string> Application::handle_write(
		const Messenger::Message& message
	) {
		std::scoped_lock lock{get_state_mutex()};

		if (message.get_header() == get_header_space().get_reset()) {
			get_logger() << Logger::Severity::information
				<< "Clearing states..."
				<< std::endl;

			get_states().clear();
		}

		get_logger() << Logger::Severity::information
			<< "Writing "
			<< message.get_data().size() / 2
			<< " key(s)..."
			<< std::endl;

		if (message.get_data().size() % 2 == 1)
			get_logger() << Logger::Severity::warning
				<< "Unpaired key \""
				<< message.get_data().back()
				<< "\" provided. "
				<< "This key will be ignored."
				<< std::endl;

		for (std::size_t i{}; i + 1 < message.get_data().size(); i += 2)
			get_states().emplace(
				message.get_data()[i],
				message.get_data()[i + 1]
			);

		broadcast(message);

		return {};
	}

	void Application::handle(const Messenger::Message& message) {
		auto handler = get_handler(message.get_header());

		if (!handler) {
			get_logger() << Logger::Severity::warning
				<< "Unhandled message: \""
				<< message.serialize()
				<< "\"..."
				<< std::endl;

			return;
		}

		get_logger() << Logger::Severity::information
			<< "Handling message: \""
			<< message.serialize()
			<< "\"..."
			<< std::endl;

		auto values = handler.value()(message);

		if (message.get_header() != get_header_space().get_response())
			get_messenger().send(
				Messenger::Message{
					get_endpoint().get_name(),
					message.get_sender_name(),
					get_header_space().get_response(),
					values,
					message.get_priority(),
					message.get_identity()
				}
			);
	}

	void Application::run() {
		Worker_pool worker_pool;

		while (get_status()) {
			auto message = get_messenger().timed_receive(
				get_endpoint().get_name()
			);

			if (!message)
				continue;

			worker_pool.work(
				std::bind(
					&Application::handle,
					this,
					message.value()
				)
			);
		}
	}
}
