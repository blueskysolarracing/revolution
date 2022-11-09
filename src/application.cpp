#include <atomic>
#include <functional>
#include <string>
#include <thread>
#include <unordered_map>

#include "application.h"
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
	    states{} {}

	void Application::run() {
		get_logger() << Logger::Severity::information
			<< "Starting: \""
			<< get_endpoint().get_name()
			<< "\"..."
			<< std::endl;

		get_status() = true;
		add_handlers();

		std::vector<std::thread> threads;  // TODO: USE THREAD POOL

		while (get_status()) {
			const auto message = get_messenger().receive(
				get_endpoint().get_name()
			);

			threads.emplace_back(&Application::handle, this, message);
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

	const Messenger& Application::get_messenger() const {
		return messenger;
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

	std::optional<const std::reference_wrapper<const std::string>>
		Application::get_state(const std::string& key) const {
		if (get_states().count(key))
			return get_states().at(key);
		else
			return std::nullopt;
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
	) const {
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
				const auto& value = get_state(key);

				if (value)
					data.push_back(get_state(key).value());
				else
					data.push_back("");
			}
		}

		return data;
	}

	std::vector<std::string> Application::handle_status(
		const Messenger::Message& message
	) const {
		get_logger() << Logger::Severity::information
			<< "Status report requested. Sending response..."
			<< std::endl;

		return {};
	}

	std::vector<std::string> Application::handle_write(
		const Messenger::Message& message
	) {
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

		std::size_t index{0};

		while (index + 1 < message.get_data().size()) {
			get_states().emplace(
				message.get_data()[index],
				message.get_data()[index + 1]
			);

			index += 2;
		}

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

	Messenger::Message Application::communicate(
		const std::string& recipient_name,
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) const {
		// TODO
	}

	std::atomic_bool& Application::get_status() {
		return status;
	}

	const Application::Handlers& Application::get_handlers() const {
		return handlers;
	}

	Application::Handlers& Application::get_handlers() {
		return handlers;
	}

	std::optional<const std::reference_wrapper<const Application::Handler>>
		Application::get_handler(const std::string& header) const {
		if (get_handlers().count(header))
			return get_handlers().at(header);
		else
			return std::nullopt;
	}

	const Application::States& Application::get_states() const {
		return states;
	}

	Application::States& Application::get_states() {
		return states;
	}

	void Application::handle(const Messenger::Message& message) const {
		if (message.get_header() == get_header_space().get_response()) {
			// TODO

			return;
		}

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
