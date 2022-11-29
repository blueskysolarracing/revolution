#include "marshal.h"

#include <functional>
#include <ostream>
#include <string>
#include <vector>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	Marshal::Marshal(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const Key_space>& key_space,
		const std::reference_wrapper<const Topology>& topology
	) : Application{header_space, key_space, topology} {}

	void Marshal::help_set_state(
		const std::string& key,
		const std::string& value
	) {
		Application::help_set_state(key, value);

		get_logger() << Logger::Severity::information
			<< "Broadcasting write to soldiers..."
			<< std::endl;

		communicate_soldiers(
			get_header_space().get_set(),
			{key, value}
		);
	}

	const Topology::Endpoint& Marshal::get_endpoint() const {
		return get_topology().get_marshal();
	}

	const Topology::Endpoint& Marshal::get_syncer() const {
		return get_topology().get_replica();
	}

	std::vector<std::string>
		Marshal::help_handle_write(const Messenger::Message& message) {
		auto data = Application::help_handle_write(message);

		get_logger() << Logger::Severity::information
			<< "Broadcasting message: \""
			<< message.serialize()
			<< "\" to soldiers..."
			<< std::endl;

		communicate_soldiers(
			message.get_header(),
			message.get_data(),
			message.get_priority()
		);

		return data;
	}

	std::vector<Messenger::Message> Marshal::communicate_soldiers(
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) {
		std::vector<Messenger::Message> messages;

		for (const auto& soldier : get_topology().get_soldiers())
			messages.push_back(
				communicate(
					soldier.get().get_name(),
					header,
					data,
					priority
				)
			);

		return messages;
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Topology topology;
	Revolution::Marshal marshal{header_space, key_space, topology};

	marshal.main();

	return 0;
}
