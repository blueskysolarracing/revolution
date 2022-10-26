#include "syncer.h"

namespace Revolution {
	Revolution::Syncer::Syncer(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space
	) : Instance{
		topology.syncer.name,
		topology.syncer.logger_configuration,
		topology.syncer.messenger_configuration,
		topology,
		header_space,
		key_space
	    }
	{
		set_handler(
			get_header_space().set,
			std::bind(&Syncer::handle_set, this, std::placeholders::_1)
		);
	}

	void Syncer::broadcast(
		const std::string& header,
		const std::vector<std::string>& data
	)
	{
		for (const auto& endpoint : get_topology().get_slaves())
			get_messenger().send(
				endpoint.messenger_configuration.name,
				header,
				data
			);
	}

	void Syncer::broadcast_state()
	{
		auto data = get_state_data();

		broadcast(get_header_space().reset, data);
	}

	void Syncer::handle_set(const Messenger::Message& message)
	{
		Instance::handle_set(message);

		broadcast_state();
	}
}

int main() {
	Revolution::Syncer syncer{
		Revolution::Topology{},
		Revolution::Header_space{},
		Revolution::Key_space{}
	};

	syncer.run();

	return 0;
}
