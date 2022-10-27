#include "configuration.h"
#include "logger.h"
#include "messenger.h"
#include "miscellaneous_controller.h"
#include "slave.h"

namespace Revolution {
	Miscellaneous_controller::Miscellaneous_controller(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		Logger& logger,
		const Messenger& messenger
	) : Slave{topology, header_space, key_space, logger, messenger}
	{
	}

	const Topology::Endpoint& Miscellaneous_controller::get_endpoint() const
	{
		return get_topology().miscellaneous_controller;
	}
}

int main() {
	Revolution::Topology topology;
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Logger logger{
		Revolution::Logger::Configuration{
			Revolution::Logger::info,
			"./" + topology.miscellaneous_controller.name + ".log"
		}
	};
	Revolution::Messenger messenger{
		Revolution::Messenger::Configuration{
			topology.miscellaneous_controller.name
		},
		logger
	};
	Revolution::Miscellaneous_controller miscellaneous_controller{
		topology,
		header_space,
		key_space,
		logger,
		messenger
	};

	miscellaneous_controller.run();

	return 0;
}
