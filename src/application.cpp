#include "application.h"

namespace Revolution {
	Application::Application(
		const std::string& name,
		const Logger::Configuration& logger_configuration,
		const Messenger::Configuration& messenger_configuration
	) : name{name},
	    logger{logger_configuration},
	    messenger{messenger_configuration, logger},
	    handlers{},
	    status{}
	{
	}

	Application::~Application()
	{
	}

	void Application::run()
	{
		get_logger() << Logger::info
			<< "Starting " << get_name() << "..." << std::endl;

		set_status(true);

		try {
			while (get_status()) {
				const auto message = get_messenger().receive();

				update(message);
			}
		} catch (std::exception& exception) {
			get_logger() << Logger::fatal
				<< "Error occurred: " << exception.what() << std::endl;
			throw exception;
		}

		get_logger() << Logger::info
			<< "Stopping " << get_name() << "..." << std::endl;
	}

	const std::string& Application::get_name() const
	{
		return name;
	}

	Logger& Application::get_logger()
	{
		return logger;
	}

	Messenger& Application::get_messenger()
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

	void Application::set_handler(const std::string& name, std::function<void(const Messenger::Message&)> handler)
	{
		if (get_handlers().count(name))
			get_logger() << Logger::warning
				<< "Overriding existing handler \"" << name << "\"..." << std::endl;
		else
			get_logger() << Logger::info
				<< "Adding handler \"" << name << "\"..." << std::endl;

		get_handlers()[name] = handler;
	}

	void Application::update(const std::optional<Messenger::Message>& optional_message)
	{
		if (optional_message.has_value())
			handle(optional_message.value());
	}

	const std::unordered_map<std::string, std::function<void(const Messenger::Message&)>>& Application::get_handlers() const
	{
		return handlers;
	}

	std::unordered_map<std::string, std::function<void(const Messenger::Message&)>>& Application::get_handlers()
	{
		return handlers;
	}

	std::optional<std::function<void(const Messenger::Message&)>> Application::get_handler(const std::string& name) const
	{
		if (get_handlers().count(name))
			return get_handlers().at(name);
		else
			return std::nullopt;
	}

	void Application::handle(const Messenger::Message& message)
	{
		auto optional_handler = get_handler(message.header);

		if (optional_handler.has_value())
			optional_handler.value()(message);
		else
			get_logger() << Logger::warning
				<< "Unhandled message: " << message.to_string() << std::endl;
	}
}
