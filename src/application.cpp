#include "application.h"

#include <atomic>
#include <condition_variable>
#include <functional>
#include <list>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>

#include "configuration.h"
#include "logger.h"
#include "messenger.h"

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
	    state_mutex{},
	    responses{},
	    response_mutex{},
	    response_condition_variable{} {}

	void Application::run() {
		get_logger() << Logger::Severity::information
			<< "Starting: \""
			<< get_endpoint().get_name()
			<< "\"..."
			<< std::endl;

		get_status() = true;
		add_handlers();

		std::list<std::thread> threads;  // TODO: USE THREAD POOL

		threads.emplace_back(&Application::sync, this);

		while (get_status()) {
			auto message = get_messenger().timed_receive(
				get_endpoint().get_name()
			);

			if (!message)
				continue;

			if (message.value().get_header()
				== get_header_space().get_response()) {
				wake(message.value());
			} else
				threads.emplace_back(
					&Application::handle,
					this,
					message.value()
				);
		}

		for (auto& thread : threads)
			thread.join();

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

	void Application::set_handler(
		const std::string& header,
		const Handler& handler
	) {
		if (get_handler(header))
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

	std::string Application::get_state(const std::string& key) {
		std::scoped_lock lock{get_state_mutex()};

		if (!get_states().count(key)) {
			get_logger() << Logger::Severity::warning
				<< "Key \""
				<< key
				<< "\" not found. "
				<< "Using empty string."
				<< std::endl;

			return "";
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
				else {
					get_logger()
						<< Logger::Severity::warning
						<< "Key \""
						<< key
						<< "\" not found. "
						<< "Using empty string."
						<< std::endl;

					data.emplace_back("");
				}
			}
		}

		return data;
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

	void Application::add_handlers() {
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
	}

	void Application::send(
		const std::string& recipient_name,
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) const {
		get_messenger().send(
			Messenger::Message{
				get_endpoint().get_name(),
				recipient_name,
				header,
				data,
				priority
			}
		);
	}

	Messenger::Message Application::communicate(
		const std::string& recipient_name,
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) {
		Messenger::Message message{
			get_endpoint().get_name(),
			recipient_name,
			header,
			data,
			priority
		};

		get_messenger().send(message);

		return sleep(message.get_identity());
	}

	const Messenger& Application::get_messenger() const {
		return messenger;
	}

	std::atomic_bool& Application::get_status() {
		return status;
	}

	const std::unordered_map<std::string, Application::Handler>&
		Application::get_handlers() const {
		return handlers;
	}

	std::unordered_map<std::string, Application::Handler>&
		Application::get_handlers() {
		return handlers;
	}

	std::optional<const std::reference_wrapper<const Application::Handler>>
		Application::get_handler(const std::string& header) const {
		if (get_handlers().count(header))
			return get_handlers().at(header);
		else
			return std::nullopt;
	}

	const std::unordered_map<std::string, std::string>&
		Application::get_states() const {
		return states;
	}

	std::unordered_map<std::string, std::string>&
		Application::get_states() {
		return states;
	}

	std::mutex& Application::get_state_mutex() {
		return state_mutex;
	}

	const std::unordered_map<unsigned int, Messenger::Message>&
		Application::get_responses() const {
		return responses;
	}

	std::unordered_map<unsigned int, Messenger::Message>&
		Application::get_responses() {
		return responses;
	}

	std::mutex& Application::get_response_mutex() {
		return response_mutex;
	}

	std::condition_variable& Application::get_response_condition_variable() {
		return response_condition_variable;
	}

	void Application::sync() {
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

	Messenger::Message Application::sleep(const unsigned int& identity) {
		std::unique_lock lock{get_response_mutex()};

		while (!get_responses().count(identity))
			get_response_condition_variable().wait(lock);

		auto message = get_responses().at(identity);

		get_responses().erase(identity);

		return message;
	}

	void Application::wake(const Messenger::Message& message) {
		std::unique_lock lock{get_response_mutex()};

		get_responses().emplace(message.get_identity(), message);

		lock.unlock();
		get_response_condition_variable().notify_all();
	}

	void Application::handle(const Messenger::Message& message) const {
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
}
