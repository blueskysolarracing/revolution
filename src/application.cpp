#include "application.h"

#include <atomic>
#include <condition_variable>
#include <cstdlib>
#include <functional>
#include <mutex>
#include <optional>
#include <ostream>
#include <string>
#include <unordered_map>
#include <vector>

#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"
#include "worker_pool.h"

namespace Revolution {
	Application::Application(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const State_space>& state_space,
		const std::reference_wrapper<const Topology>& topology,
		const std::string& name
	) : header_space{header_space},
	    state_space{state_space},
	    topology{topology},
	    name{name},
	    logger{},
	    messenger{},
	    heart{},
	    worker_pool{},
	    status{},
	    handlers{},
	    handler_mutex{},
	    responses{},
	    response_mutex{},
	    response_condition_variable{} {}

	Application::~Application() {
		Messenger::unlink(get_name());
	}

	void Application::main() {
		get_logger() << Logger::Severity::information
			<< "Starting: \""
			<< get_name()
			<< "\"..."
			<< std::endl;

		setup();
		run();

		get_logger() << Logger::Severity::information
			<< "Stopping: \""
			<< get_name()
			<< "\"..."
			<< std::endl;
	}

	const Header_space& Application::get_header_space() const {
		return header_space;
	}

	const State_space& Application::get_state_space() const {
		return state_space;
	}

	const Topology& Application::get_topology() const {
		return topology;
	}

	const std::string& Application::get_name() const {
		return name;
	}

	const Logger& Application::get_logger() const {
		return logger;
	}

	const Worker_pool& Application::get_worker_pool() const {
		return worker_pool;
	}

	const std::atomic_bool& Application::get_status() const {
		return status;
	}

	Worker_pool& Application::get_worker_pool() {
		return worker_pool;
	}

	std::atomic_bool& Application::get_status() {
		return status;
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

		get_handlers()[header] = handler;
	}

	Messenger::Message Application::send(
		const std::string& recipient_name,
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) const {
		Messenger::Message message{
			get_name(),
			recipient_name,
			header,
			data,
			priority
		};

		get_logger() << Logger::Severity::information
			<< "Sending message: \""
			<< message.serialize()
			<< "\"..."
			<< std::endl;

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
			get_header_space().get_abort(),
			std::bind(
				&Application::handle_abort,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_exit(),
			std::bind(
				&Application::handle_exit,
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
			get_header_space().get_status(),
			std::bind(
				&Application::handle_status,
				this,
				std::placeholders::_1
			)
		);
	}

	const Messenger& Application::get_messenger() const {
		return messenger;
	}

	const Heart& Application::get_heart() const {
		return heart;
	}

	const std::unordered_map<std::string, Application::Handler>&
		Application::get_handlers() const {
		return handlers;
	}

	const std::mutex& Application::get_handler_mutex() const {
		return handler_mutex;
	}

	const std::unordered_map<
		unsigned int,
		std::optional<Messenger::Message>
	>& Application::get_responses() const {
		return responses;
	}

	const std::mutex& Application::get_response_mutex() const {
		return response_mutex;
	}

	const std::condition_variable&
		Application::get_response_condition_variable() const {
		return response_condition_variable;
	}

	Heart& Application::get_heart() {
		return heart;
	}

	std::unordered_map<std::string, Application::Handler>&
		Application::get_handlers() {
		return handlers;
	}

	std::mutex& Application::get_handler_mutex() {
		return handler_mutex;
	}

	std::unordered_map<unsigned int, std::optional<Messenger::Message>>&
		Application::get_responses() {
		return responses;
	}

	std::mutex& Application::get_response_mutex() {
		return response_mutex;
	}

	std::condition_variable& Application::get_response_condition_variable() {
		return response_condition_variable;
	}

	std::optional<const std::reference_wrapper<const Application::Handler>>
		Application::get_handler(const std::string& header) {
		std::scoped_lock lock{get_handler_mutex()};

		if (!get_handlers().count(header))
			return std::nullopt;

		return get_handlers().at(header);
	}

	Messenger::Message
		Application::get_response(const Messenger::Message& message) {
		std::unique_lock lock{get_response_mutex()};

		get_responses().emplace(message.get_identity(), std::nullopt);

		while (!get_responses().at(message.get_identity()))
			get_response_condition_variable().wait(lock);

		auto response
			= get_responses().at(message.get_identity()).value();

		get_responses().erase(message.get_identity());

		return response;
	}

	void Application::set_response(const Messenger::Message& message) {
		std::unique_lock lock{get_response_mutex()};

		if (get_responses().count(message.get_identity())) {
			get_responses().erase(message.get_identity());
			get_responses().emplace(
				message.get_identity(),
				message
			);
		}

		get_response_condition_variable().notify_all();
	}

	std::vector<std::string>
		Application::handle_abort(const Messenger::Message& message) {
		if (!message.get_data().empty()) {
			get_logger() << Logger::Severity::error
				<< "Abort expects no arguments, but "
				<< message.get_data().size()
				<< " argument(s) were supplied. "
				<< "This message will be ignored."
				<< std::endl;
			
			return {};
		}

		get_logger() << Logger::Severity::information
			<< "Aborting..."
			<< std::endl;

		std::abort();

		return {};
	}

	std::vector<std::string>
		Application::handle_exit(const Messenger::Message& message) {
		if (!message.get_data().empty()) {
			get_logger() << Logger::Severity::error
				<< "Exit expects no arguments, but "
				<< message.get_data().size()
				<< " argument(s) were supplied. "
				<< "This message will be ignored."
				<< std::endl;

			return {};
		}

		get_logger() << Logger::Severity::information
			<< "Exiting gracefully..."
			<< std::endl;

		get_status() = false;

		return {};
	}

	std::vector<std::string> Application::handle_response(
		const Messenger::Message& message
	) {
		get_logger() << Logger::Severity::information
			<< "Waking up a corresponding thread (if any)..."
			<< std::endl;

		set_response(message);

		return {};
	}

	std::vector<std::string>
		Application::handle_status(const Messenger::Message& message) const {
		if (!message.get_data().empty())
			get_logger() << Logger::Severity::warning
				<< "Status expects no arguments, but "
				<< message.get_data().size()
				<< " argument(s) were supplied. "
				<< "The argument(s) will be ignored."
				<< std::endl;

		get_logger() << Logger::Severity::information
			<< "Status report requested. Sending response..."
			<< std::endl;

		return {};
	}

	void Application::handle(const Messenger::Message& message) {
		if (message.get_header() == get_header_space().get_response()) {
			handle_response(message);

			return;
		}

		get_worker_pool().work(
			std::bind(&Application::help_handle, this, message)
		);
	}

	void Application::help_handle(const Messenger::Message& message) {
		auto handler = get_handler(message.get_header());

		if (!handler) {
			get_logger() << Logger::Severity::warning
				<< "Skipping handling of message: \""
				<< message.serialize()
				<< "\"..."
				<< std::endl;

			return;
		}

		auto data = handler.value()(message);

		Messenger::Message response{
			get_name(),
			message.get_sender_name(),
			get_header_space().get_response(),
			data,
			message.get_priority(),
			message.get_identity()
		};

		get_logger() << Logger::Severity::information
			<< "Sending response: \""
			<< response.serialize()
			<< "\"..."
			<< std::endl;

		get_messenger().send(response);
	}

	void Application::run() {
		while (get_status()) {
			auto message
				= get_messenger().timed_receive(get_name());

			if (message) {
				get_logger() << Logger::Severity::information
					<< "Received message: \""
					<< message.value().serialize()
					<< "\"."
					<< std::endl;

				handle(message.value());
			}

			get_heart().beat();
		}
	}
}
