#include <chrono>

#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"
#include "miscellaneous_controller.h"
#include "soldier.h"

namespace Revolution {
	Miscellaneous_controller::Miscellaneous_controller(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		const Logger& logger,
		const Messenger& messenger,
		Heart& heart
	) : Soldier{
		topology,
		header_space,
		key_space,
		logger,
		messenger,
		heart
	    }
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
	Revolution::Logger logger{Revolution::Logger::Configuration{}};
	Revolution::Messenger messenger{
		Revolution::Messenger::Configuration{
			topology.miscellaneous_controller.name
		},
		logger
	};
	Revolution::Heart heart{
		Revolution::Heart::Configuration{
			std::chrono::seconds(1),
			[&messenger, &topology, &header_space] () {
				messenger.send(
					topology.miscellaneous_controller.name,
					header_space.heartbeat
				);
			}
		},
		logger
	};
	Revolution::Miscellaneous_controller miscellaneous_controller{
		topology,
		header_space,
		key_space,
		logger,
		messenger,
		heart
	};

	miscellaneous_controller.run();

	return 0;
}
