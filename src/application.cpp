#include "application.h"

namespace Revolution {
	Application::Application(const Instance &instance)
		: instance{instance},
		  logger{instance.get_log_level(), instance.get_log_filename()},
		  messenger{instance.get_name(), instance.get_priority(), logger}
	{
		get_logger().log(Log_level::info, "Starting " + get_instance().get_name() + "...");
	}

	Application::~Application() {
		get_logger().log(Log_level::info, "Exiting " + get_instance().get_name() + "...");
	}

	void Application::run() {
		try {
		} catch (std::exception &exception) {
			get_logger().log(Log_level::fatal, exception.what());
			throw exception;
		}
	}

	const Instance &Application::get_instance() const
	{
		return instance;
	}

	Logger &Application::get_logger()
	{
		return logger;
	}

	Messenger &Application::get_messenger()
	{
		return messenger;
	}
}
