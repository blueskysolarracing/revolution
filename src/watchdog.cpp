#include "watchdog.h"

namespace Revolution {
	Revolution::Watchdog::Watchdog(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space
	) : Instance{
		topology.watchdog.name,
		topology.watchdog.logger_configuration,
		topology.watchdog.messenger_configuration,
		topology,
		header_space,
		key_space
	    }
	{
		set_handler(
			get_header_space().exit,
			std::bind(&Watchdog::handle_exit, this, std::placeholders::_1)
		);
	}

	void Watchdog::run()
	{
		get_logger() << Logger::info
			<< "Spawning endpoints..." << std::endl;

		for (const auto& endpoint : get_topology().get_endpoints())
			if (endpoint.name != get_name() && !is_running(endpoint)) {
				stop(endpoint);
				start(endpoint);
			}

		get_messenger().send(
			get_topology().get_master().messenger_configuration.name,
			get_header_space().sync
		);

		get_logger() << Logger::info
			<< "Starting " << get_name() << "..." << std::endl;

		set_status(true);

		try {
			while (get_status()) {
				const auto message = get_messenger().receive(
					std::chrono::system_clock::now() + std::chrono::seconds(5)
				);

				update(message);
			}
		} catch (std::exception& exception) {
			get_logger() << Logger::fatal
				<< "Error occurred: " << exception.what() << std::endl;
			throw exception;
		}

		get_logger() << Logger::info
			<< "Stopping " << get_name() << "..." << std::endl;

		get_logger() << Logger::info
			<< "Stopping endpoints..." << std::endl;

		for (const auto& endpoint : get_topology().get_endpoints())
			if (endpoint.name != get_name())
				stop(endpoint);
	}

	void Watchdog::update(const std::optional<Messenger::Message>& optional_message)
	{
		Instance::update(optional_message);

		for (const auto& endpoint : get_topology().get_endpoints())
			if (endpoint.name != get_name() && !is_running(endpoint)) {
				stop(endpoint);
				start(endpoint);
			}
	}

	bool Watchdog::is_running(const Topology::Endpoint& endpoint)
	{
		get_messenger().send(
			std::chrono::system_clock::now() + std::chrono::milliseconds(1000),
			endpoint.messenger_configuration.name,
			get_header_space().status
		);
		auto optional_message = get_messenger().receive(
			std::chrono::system_clock::now() + std::chrono::milliseconds(1000)
		);

		return optional_message.has_value();
	}

	void Watchdog::start(const Topology::Endpoint& endpoint)
	{
		get_logger() << Logger::info
			<< "Starting the endpoint for " + endpoint.name << std::endl;

		int ret = system(endpoint.get_command().data());

		if (ret == -1)
			get_logger() << Logger::error
				<< "A child process could not be created to start the endpoint. (errno = "
				<< errno << ')' << std::endl;
		else {
			get_logger() << Logger::info
				<< "Successfully Started the endpoint for " + endpoint.name << std::endl;

			get_messenger().send(
				endpoint.messenger_configuration.name,
				get_header_space().reset,
				get_state_data()
			);
		}
	}

	void Watchdog::stop(const Topology::Endpoint& endpoint)
	{
		get_logger() << Logger::info
			<< "Stopping the endpoint for " + endpoint.name << std::endl;

		get_messenger().send(
			std::chrono::system_clock::now() + std::chrono::milliseconds(100),
			endpoint.messenger_configuration.name,
			get_header_space().exit
		);

		std::string command = "pkill -f " + endpoint.binary_filename;
		int ret = system(command.data());

		if (ret == -1)
			get_logger() << Logger::error
				<< "A child process could not be created to stop the endpoint. (errno = "
				<< errno << ')' << std::endl;
		else
			get_logger() << Logger::info
				<< "Successfully Stopped the endpoint for " + endpoint.name << std::endl;
	}
}

int main() {
	Revolution::Watchdog watchdog{
		Revolution::Topology{},
		Revolution::Header_space{},
		Revolution::Key_space{}
	};

	watchdog.run();

	return 0;
}

