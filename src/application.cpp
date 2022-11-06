#include <functional>
#include <string>
#include <unordered_map>

#include <stdlib.h>
#include <unistd.h>

#include "application.h"
#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"

namespace Revolution {
	Application::Application(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		const Logger& logger,
		const Messenger& messenger,
		Heart& heart
	) : topology{topology},
	    header_space{header_space},
	    key_space{key_space},
	    logger{logger},
	    messenger{messenger},
	    heart{heart},
	    status{},
	    handlers{},
	    states{}
	{
		set_handler(
			get_header_space().exit,
			std::bind(
				&Application::handle_exit,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get,
			std::bind(
				&Application::handle_read,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().hang,
			std::bind(
				&Application::handle_hang,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().heartbeat,
			std::bind(
				&Application::handle_heartbeat,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().reset,
			std::bind(
				&Application::handle_write,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().set,
			std::bind(
				&Application::handle_write,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().status,
			std::bind(
				&Application::handle_status,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().sync,
			std::bind(
				&Application::handle_sync,
				this,
				std::placeholders::_1
			)
		);
	}

	void Application::run()
	{
		get_logger() << Logger::information
			<< "Starting "
			<< get_endpoint().name
			<< "..."
			<< std::endl;

		set_status(true);

		try {
			while (get_status()) {
				const auto message = get_messenger().receive();

				handle(message);
			}
		} catch (std::exception& exception) {
			get_logger() << Logger::alert
				<< "Error occurred: "
				<< exception.what()
				<< std::endl;

			throw;
		}

		get_logger() << Logger::information
			<< "Stopping "
			<< get_endpoint().name
			<< "..."
			<< std::endl;
	}

	const Topology& Application::get_topology() const
	{
		return topology;
	}

	const Header_space& Application::get_header_space() const
	{
		return header_space;
	}

	const Key_space& Application::get_key_space() const
	{
		return key_space;
	}

	const Logger& Application::get_logger() const
	{
		return logger;
	}

	const Messenger& Application::get_messenger() const
	{
		return messenger;
	}

	Heart& Application::get_heart() const
	{
		return heart;
	}

	const bool& Application::get_status() const
	{
		return status;
	}

	void Application::set_status(const bool& status)
	{
		this->status = status;
	}

	const Application::States& Application::get_states() const
	{
		return states;
	}

	std::vector<std::string> Application::get_state_data() const
	{
		std::vector<std::string> data;

		for (const auto& [key, value] : get_states()) {
			data.push_back(key);
			data.push_back(value);
		}

		return data;
	}

	void Application::set_handler(
		const std::string& name,
		const Handler& handler
	)
	{
		if (get_handlers().count(name))
			get_logger() << Logger::warning
				<< "Overriding an existing handler: \""
				<< name
				<< "\"..."
				<< std::endl;
		else
			get_logger() << Logger::information
				<< "Adding handler: \""
				<< name
				<< "\"..."
				<< std::endl;

		get_handlers().emplace(name, handler);
	}

	void Application::handle_exit(const Messenger::Message& message)
	{
		if (message.data.size() > 1)
			get_logger() << Logger::warning
				<< "Received multiple arguments for exit. "
				<< "Only the first will be used as exit code. "
				<< "The rest will be ignored."
				<< std::endl;

		if (message.data.empty()) {
			get_logger() << Logger::information
				<< "Exiting gracefully..."
				<< std::endl;

			set_status(false);
		} else {
			int error_code = std::stoi(message.data.front());

			get_logger() << Logger::information
				<< "Exiting immediately with error code: "
				<< error_code
				<< "..."
				<< std::endl;

			exit(error_code);
		}
	}

	void Application::handle_hang(const Messenger::Message& message) const
	{
		get_logger() << Logger::information
			<< "Hanging indefinitely..."
			<< std::endl;

		pause();
	}

	void Application::handle_heartbeat(
		const Messenger::Message& message
	) const
	{
		get_logger() << Logger::information
			<< "Beating heart..."
			<< std::endl;

		get_heart().beat();
	}

	void Application::handle_read(const Messenger::Message& message) const
	{
		get_logger() << Logger::information
			<< "Reading "
			<< message.data.size()
			<< " key(s)..."
			<< std::endl;

		std::vector<std::string> data;

		for (const auto& datum : message.data)
			if (get_states().count(datum))
				data.push_back(get_states().at(datum));
			else
				data.push_back("");

		get_messenger().send(
			message.sender_name,
			get_header_space().response,
			data
		);
	}

	void Application::handle_status(const Messenger::Message& message) const
	{
		get_logger() << Logger::information
			<< "Status report requested. Sending response..."
			<< std::endl;

		get_messenger().send(
			message.sender_name,
			get_header_space().response
		);
	}

	void Application::handle_sync(const Messenger::Message& message) const
	{
		get_logger() << Logger::information
			<< "Sync requested. Resetting requester's data..."
			<< std::endl;

		get_messenger().send(
			message.sender_name,
			get_header_space().reset,
			get_state_data()
		);
	}

	void Application::handle_write(const Messenger::Message& message)
	{
		if (message.header == get_header_space().reset) {
			get_logger() << Logger::information
				<< "Clearing database..."
				<< std::endl;

			get_states().clear();
		}

		get_logger() << Logger::information
			<< "Writing "
			<< message.data.size() / 2
			<< " key(s)..."
			<< std::endl;

		if (message.data.size() % 2 == 1)
			get_logger() << Logger::warning
				<< "Unpaired key \""
				<< message.data.back()
				<< "\" provided. "
				<< "This key will be ignored."
				<< std::endl;

		for (unsigned int i = 0; i + 1 < message.data.size(); i += 2)
			get_states().emplace(
				message.data[i],
				message.data[i + 1]
			);
	}

	const Application::Handlers& Application::get_handlers() const
	{
		return handlers;
	}

	Application::Handlers& Application::get_handlers()
	{
		return handlers;
	}

	Application::States& Application::get_states()
	{
		return states;
	}

	void Application::handle(const Messenger::Message& message) const
	{
		if (get_handlers().count(message.header)) {
			get_logger() << Logger::information
				<< "Handling message: "
				<< message.to_string()
				<< std::endl;

			return get_handlers().at(message.header)(message);
		} else
			get_logger() << Logger::warning
				<< "Unhandled message: "
				<< message.to_string()
				<< std::endl;
	}
}
