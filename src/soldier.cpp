#include "soldier.h"

#include <functional>
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

	const Topology::Endpoint& Soldier::get_syncer() const {
		return get_topology().get_marshal();
	}

	void Soldier::broadcast(
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) const {
		send_marshal(header, data, priority);
	}

	void Soldier::broadcast(
		const Messenger::Message& message
	) const {
		if (message.get_sender_name()
			!= get_topology().get_marshal().get_name())
			send_marshal(
				message.get_header(),
				message.get_data(),
				message.get_priority()
			);
	}

	Messenger::Message Soldier::send_marshal(
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) const {
		return send(
			get_topology().get_marshal().get_name(),
			header,
			data,
			priority
		);
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
}
