#include "soldier.h"

#include <functional>
#include <ostream>
#include <string>
#include <vector>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	Soldier::Soldier(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const Key_space>& key_space,
		const std::reference_wrapper<const Topology>& topology
	) : Application{header_space, key_space, topology} {}

	void Soldier::set_state(
		const std::string& key,
		const std::string& value
	) {
		get_logger() << Logger::Severity::information
			<< "Passing write to marshal..."
			<< std::endl;

		communicate_marshal(get_header_space().get_set(), {key, value});
	}

	const Topology::Endpoint& Soldier::get_syncer() const {
		return get_topology().get_marshal();
	}

	std::vector<std::string>
		Soldier::handle_write(const Messenger::Message& message) {
		if (message.get_sender_name()
			== get_topology().get_marshal().get_name())
			return Application::handle_write(message);

		get_logger() << Logger::Severity::information
			<< "Passing message: \""
			<< message.serialize()
			<< "\" to marshal..."
			<< std::endl;

		auto data = communicate_marshal(
			message.get_header(),
			message.get_data(),
			message.get_priority()
		).get_data();

		return data;
	}

	Messenger::Message Soldier::communicate_marshal(
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) {
		return communicate(
			get_topology().get_marshal().get_name(),
			header,
			data,
			priority
		);
	}

	void Soldier::add_handlers() {
		Application::add_handlers();

		set_handler(
			get_header_space().get_set(),
			std::bind(
				&Soldier::handle_write,
				this,
				std::placeholders::_1
			)
		);
	}
}
