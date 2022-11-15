#include "marshal.h"

#include "application.h"
#include "configuration.h"

namespace Revolution {
	Marshal::Marshal(
		const Header_space& header_space,
		const Key_space& key_space,
		const Topology& topology
	) : Application{header_space, key_space, topology} {}

	const Topology::Endpoint& Marshal::get_endpoint() const {
		return get_topology().get_marshal();
	}

	const Topology::Endpoint& Marshal::get_syncer() const {
		return get_topology().get_replica();
	}

	void Marshal::broadcast(
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) const {
		send_soldiers(header, data, priority);
	}

	void Marshal::broadcast(
		const Messenger::Message& message
	) const {
		send_soldiers_except(
			message.get_sender_name(),
			message.get_header(),
			message.get_data(),
			message.get_priority()
		);
	}

	void Marshal::send_soldiers(
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) const {
		for (const auto& soldier : get_topology().get_soldiers())
			send(soldier.get().get_name(), header, data, priority);
	}

	void Marshal::send_soldiers_except(
		const std::string& recipient_name,
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) const {
		for (const auto& soldier : get_topology().get_soldiers())
			if (soldier.get().get_name() != recipient_name)
				send(
					soldier.get().get_name(),
					header,
					data,
					priority
				);
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

	std::vector<std::optional<Messenger::Message>>
		Marshal::communicate_soldiers_except(
		const std::string& recipient_name,
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) {
		std::vector<std::optional<Messenger::Message>> messages;

		for (const auto& soldier : get_topology().get_soldiers()) {
			if (soldier.get().get_name() == recipient_name)
				messages.push_back(std::nullopt);
			else
				messages.push_back(
					communicate(
						soldier.get().get_name(),
						header,
						data,
						priority
					)
				);
		}

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
