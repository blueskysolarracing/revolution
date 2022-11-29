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
		const std::reference_wrapper<const Key_space>& key_space,
		const std::reference_wrapper<const Topology>& topology
	) : header_space{header_space},
	    key_space{key_space},
	    topology{topology},
	    logger{},
	    messenger{},
	    heart{},
	    worker_pool{},
	    status{},
	    handlers{},
	    watchers{},
	    states{},
	    responses{},
	    handler_mutex{},
	    watcher_mutex{},
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

	const Heart& Application::get_heart() const {
		return heart;
	}

	const Worker_pool& Application::get_worker_pool() const {
		return worker_pool;
	}

	const std::atomic_bool& Application::get_status() const {
		return status;
	}

	Heart& Application::get_heart() {
		return heart;
	}

	Worker_pool& Application::get_worker_pool() {
		return worker_pool;
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

		get_handlers()[header] = handler;
	}

	std::optional<const std::reference_wrapper<const Application::Watcher>>
		Application::get_watcher(const std::string& key) {
		std::scoped_lock lock{get_watcher_mutex()};

		if (!get_watchers().count(key))
			return std::nullopt;

		return get_watchers().at(key);
	}

	void Application::set_watcher(
		const std::string& key,
		const Watcher& watcher
	) {
		std::scoped_lock lock{get_watcher_mutex()};

		if (get_watchers().count(key))
			get_logger() << Logger::Severity::warning
				<< "Overriding an existing watcher: \""
				<< key
				<< "\"..."
				<< std::endl;
		else
			get_logger() << Logger::Severity::information
				<< "Adding watcher: \""
				<< key
				<< "\"..."
				<< std::endl;

		get_watchers()[key] = watcher;
	}

	std::optional<std::string>
		Application::get_state(const std::string& key) {
		get_logger() << Logger::Severity::information
			<< "Locking states..."
			<< std::endl;

		std::scoped_lock lock{get_state_mutex()};

		get_logger() << Logger::Severity::information
			<< "Locked states."
			<< std::endl;

		if (!get_states().count(key)) {
			get_logger() << Logger::Severity::warning
				<< "Key \""
				<< key
				<< "\" not found. "
				<< "Using std::nullopt."
				<< std::endl;

			return std::nullopt;
		}

		get_logger() << Logger::Severity::information
			<< "Unlocking states..."
			<< std::endl;

		return get_states().at(key);
	}

	void Application::set_state(
		const std::string& key,
		const std::string& value
	) {
		get_logger() << Logger::Severity::information
			<< "Locking states..."
			<< std::endl;

		std::scoped_lock lock{get_state_mutex()};

		get_logger() << Logger::Severity::information
			<< "Locked states."
			<< std::endl;

		help_set_state(key, value);

		get_logger() << Logger::Severity::information
			<< "Unlocking states..."
			<< std::endl;
	}

	void Application::help_set_state(
		const std::string& key,
		const std::string& value
	) {
		get_states()[key] = value;

		auto watcher = get_watcher(key);

		if (watcher)
			watcher.value()(key, value);
	}

	std::vector<std::string>
		Application::handle_abort(const Messenger::Message& message) {
		if (!message.get_data().empty())
			get_logger() << Logger::Severity::warning
				<< "Abort expects no arguments, "
				<< "but at least one was supplied. "
				<< "They will be ignored."
				<< std::endl;

		get_logger() << Logger::Severity::information
			<< "Aborting..."
			<< std::endl;

		std::abort();
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

	std::vector<std::string>
		Application::handle_read(const Messenger::Message& message) {
		get_logger() << Logger::Severity::information
			<< "Locking states..."
			<< std::endl;

		std::scoped_lock lock{get_state_mutex()};
		std::vector<std::string> data;

		get_logger() << Logger::Severity::information
			<< "Locked states."
			<< std::endl;

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
				if (get_states().count(key)) {
					data.push_back(key);
					data.push_back(get_states().at(key));
				} else
					get_logger()
						<< Logger::Severity::warning
						<< "Key \""
						<< key
						<< "\" not found. "
						<< "Ignoring key..."
						<< std::endl;
			}
		}

		get_logger() << Logger::Severity::information
			<< "Unlocking states..."
			<< std::endl;

		return data;
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
				<< "Status expects no arguments, "
				<< "but at least one was supplied. "
				<< "They will be ignored."
				<< std::endl;

		get_logger() << Logger::Severity::information
			<< "Status report requested. Sending response..."
			<< std::endl;

		return {};
	}

	std::vector<std::string>
		Application::handle_write(const Messenger::Message& message) {
		get_logger() << Logger::Severity::information
			<< "Locking states..."
			<< std::endl;

		std::scoped_lock lock{get_state_mutex()};

		get_logger() << Logger::Severity::information
			<< "Locked states."
			<< std::endl;

		auto data = help_handle_write(message);

		get_logger() << Logger::Severity::information
			<< "Unlocking states..."
			<< std::endl;

		return data;
	}

	std::vector<std::string> Application::help_handle_write(
		const Messenger::Message& message
	) {
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
			help_set_state(
				message.get_data()[i],
				message.get_data()[i + 1]
			);

		return {};
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

	void Application::add_handlers() {
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
			get_header_space().get_get(),
			std::bind(
				&Application::handle_read,
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
	}

	void Application::add_watchers() {
		get_logger() << Logger::Severity::information
			<< "Adding watchers..."
			<< std::endl;
	}

	void Application::setup() {
		get_status() = true;
		add_handlers();
		add_watchers();
		get_worker_pool().work(std::bind(&Application::sync, this));
	}

	const Messenger& Application::get_messenger() const {
		return messenger;
	}

	const std::unordered_map<std::string, Application::Handler>&
		Application::get_handlers() const {
		return handlers;
	}

	const std::unordered_map<std::string, Application::Watcher>&
		Application::get_watchers() const {
		return watchers;
	}

	const std::unordered_map<std::string, std::string>&
		Application::get_states() const {
		return states;
	}

	const std::unordered_map<
		unsigned int,
		std::optional<Messenger::Message>
	>&
		Application::get_responses() const {
		return responses;
	}

	const std::mutex& Application::get_handler_mutex() const {
		return handler_mutex;
	}

	const std::mutex& Application::get_watcher_mutex() const {
		return watcher_mutex;
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

	std::unordered_map<std::string, Application::Watcher>&
		Application::get_watchers() {
		return watchers;
	}

	std::unordered_map<std::string, std::string>&
		Application::get_states() {
		return states;
	}

	std::unordered_map<unsigned int, std::optional<Messenger::Message>>&
		Application::get_responses() {
		return responses;
	}

	std::mutex& Application::get_handler_mutex() {
		return handler_mutex;
	}

	std::mutex& Application::get_watcher_mutex() {
		return watcher_mutex;
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

		get_logger() << Logger::Severity::information
			<< "Sending message: \""
			<< message.serialize()
			<< "\"..."
			<< std::endl;

		get_messenger().send(message);

		return message;
	}

	void Application::sync() {
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
				get_header_space().get_set(),
				message.get_data(),
				message.get_priority(),
				message.get_identity()
			}
		);
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
			get_endpoint().get_name(),
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
			auto message = get_messenger().timed_receive(
				get_endpoint().get_name()
			);

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
