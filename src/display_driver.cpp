#include <chrono>

#include "configuration.h"
#include "display_driver.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"
#include "soldier.h"

namespace Revolution {
	Display_driver::Display_driver(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		Logger& logger,
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

	const Topology::Endpoint& Display_driver::get_endpoint() const
	{
		return get_topology().display_driver;
	}
}

int main() {
	Revolution::Topology topology;
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Logger logger{
		Revolution::Logger::Configuration{
			Revolution::Logger::info
		}
	};
	Revolution::Messenger messenger{
		Revolution::Messenger::Configuration{
			topology.display_driver.name
		},
		logger
	};
	Revolution::Heart heart{
		Revolution::Heart::Configuration{
			std::chrono::seconds(1),
			[&messenger, &topology, &header_space] () {
				messenger.send(
					topology.display_driver.name,
					header_space.heartbeat
				);
			},
		},
		logger
	};
	Revolution::Display_driver display_driver{
		topology,
		header_space,
		key_space,
		logger,
		messenger,
		heart
	};

	display_driver.run();

	return 0;
}
