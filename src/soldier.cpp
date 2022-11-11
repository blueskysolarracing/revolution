#include "soldier.h"

#include <functional>

#include "application.h"
#include "configuration.h"
#include "logger.h"
#include "messenger.h"

namespace Revolution {
	Soldier::Soldier(
		const Header_space& header_space,
		const Key_space& key_space,
		const Topology& topology
	) : Application{header_space, key_space, topology} {}

	void Soldier::set_state(
		const std::string& key,
		const std::string& value
	) {
		Application::set_state(key, value);

		communicate_with_marshal(
			get_header_space().get_set(),
			{key, value}
		);
	}

	std::vector<std::string> Soldier::handle_write(
		const Messenger::Message& message
	) {
		auto values = Application::handle_write(message);

		if (message.get_sender_name()
			!= get_topology().get_marshal().get_name())
			communicate_with_marshal(
				message.get_header(),
				message.get_data(),
				message.get_priority()
			);

		return values;
	}

	void Soldier::add_handlers() {
		Application::add_handlers();

		set_handler(
			get_header_space().get_reset(),
			std::bind(
				&Soldier::handle_write,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_set(),
			std::bind(
				&Soldier::handle_write,
				this,
				std::placeholders::_1
			)
		);
	}

	Messenger::Message Soldier::communicate_with_marshal(
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
}
