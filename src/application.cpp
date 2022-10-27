#include <functional>
#include <string>
#include <unordered_map>

#include <unistd.h>

#include "application.h"
#include "configuration.h"
#include "logger.h"
#include "messenger.h"

namespace Revolution {
	Application::Application(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		Logger& logger,
		const Messenger& messenger
	) : topology{topology},
	    header_space{header_space},
	    key_space{key_space},
	    logger{logger},
	    messenger{messenger},
	    status{},
	    handlers{},
	    states{}
	{
		set_handler(
			get_header_space().status,
			std::bind(
				&Application::handle_status,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get,
			std::bind(
				&Application::handle_get,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().set,
			std::bind(
				&Application::handle_set,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().reset,
			std::bind(
				&Application::handle_reset,
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
		set_handler(
			get_header_space().hang,
			std::bind(
				&Application::handle_hang,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().exit,
			std::bind(
				&Application::handle_exit,
				this,
				std::placeholders::_1
			)
		);
	}

	void Application::run()
	{
		get_logger() << Logger::info
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
			get_logger() << Logger::fatal
				<< "Error occurred: "
				<< exception.what()
				<< std::endl;

			throw exception;
		}

		get_logger() << Logger::info
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

	Logger& Application::get_logger() const
	{
		return logger;
	}

	const Messenger& Application::get_messenger() const
	{
		return messenger;
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
			get_logger() << Logger::info
				<< "Adding handler: \""
				<< name
				<< "\"..."
				<< std::endl;

		get_handlers().emplace(name, handler);
	}

	void Application::handle_status(const Messenger::Message& message) const
	{
		get_messenger().send(
			message.sender_name,
			get_header_space().response
		);
	}

	void Application::handle_get(const Messenger::Message& message) const
	{
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

	void Application::handle_set(const Messenger::Message& message)
	{
		if (message.data.size() % 2 == 1)
			get_logger() << Logger::error
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

	void Application::handle_reset(const Messenger::Message& message)
	{
		get_states().clear();

		handle_set(message);
	}

	void Application::handle_sync(const Messenger::Message& message) const
	{
		get_messenger().send(
			message.sender_name,
			get_header_space().reset,
			get_state_data()
		);
	}

	void Application::handle_hang(const Messenger::Message& message) const
	{
		pause();
	}

	void Application::handle_exit(const Messenger::Message& message)
	{
		set_status(false);
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
		if (get_handlers().count(message.header))
			return get_handlers().at(message.header)(message);
		else
			get_logger() << Logger::warning
				<< "Unhandled message: "
				<< message.to_string()
				<< std::endl;
	}
}
