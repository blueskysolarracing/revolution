#include "instance.h"

namespace Revolution {
	Instance::Instance(
		const std::string& name,
		const Logger::Configuration& logger_configuration,
		const Messenger::Configuration& messenger_configuration,
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space
	) : Application{name, logger_configuration, messenger_configuration},
	    topology{topology},
	    header_space{header_space},
	    key_space{key_space},
	    states{}
	{
		set_handler(
			get_header_space().get,
			std::bind(&Instance::handle_get, this, std::placeholders::_1)
		);
		set_handler(
			get_header_space().set,
			std::bind(&Instance::handle_set, this, std::placeholders::_1)
		);
		set_handler(
			get_header_space().reset,
			std::bind(&Instance::handle_reset, this, std::placeholders::_1)
		);
		set_handler(
			get_header_space().exit,
			std::bind(&Instance::handle_exit, this, std::placeholders::_1)
		);
	}

	const Topology& Instance::get_topology() const
	{
		return topology;
	}

	const Header_space& Instance::get_header_space() const
	{
		return header_space;
	}

	const Key_space& Instance::get_key_space() const
	{
		return key_space;
	}

	const std::unordered_map<std::string, std::string>& Instance::get_states() const
	{
		return states;
	}

	std::unordered_map<std::string, std::string>& Instance::get_states()
	{
		return states;
	}

	std::vector<std::string> Instance::get_state_data() const
	{
		std::vector<std::string> data;

		for (const auto& [key, value] : get_states()) {
			data.push_back(key);
			data.push_back(value);
		}

		return data;
	}

	void Instance::handle_get(const Messenger::Message& message)
	{
		std::vector<std::string> data;

		for (const auto& datum : message.data)
			data.push_back(get_states()[datum]);

		get_messenger().send(message.sender_name, get_header_space().response, data);
	}

	void Instance::handle_set(const Messenger::Message& message)
	{
		if (message.data.size() % 2 == 1)
			get_logger() << Logger::warning
				<< "Unpaired key \"" << message.data.back() << "\" provided. "
				<< "This key will be ignored." << std::endl;

		for (unsigned int i = 0; i < message.data.size(); i += 2)
			get_states()[message.data[i]] = message.data[i + 1];
	}

	void Instance::handle_reset(const Messenger::Message& message)
	{
		get_states().clear();

		handle_set(message);
	}

	void Instance::handle_exit(const Messenger::Message& message)
	{
		set_status(false);
	}
}
