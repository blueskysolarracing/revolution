#include <string>

#include "configuration.h"
#include "display_driver.h"
#include "logger.h"
#include "messenger.h"
#include "slave.h"

namespace Revolution {
	Display_driver::Display_driver(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		Logger& logger,
		const Messenger& messenger
	) : Slave{topology, header_space, key_space, logger, messenger}
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
			Revolution::Logger::info,
			"./" + topology.display_driver.name + ".log"
		}
	};
	Revolution::Messenger messenger{
		Revolution::Messenger::Configuration{
			topology.display_driver.name
		},
		logger
	};
	Revolution::Display_driver display_driver{
		topology,
		header_space,
		key_space,
		logger,
		messenger
	};

	display_driver.run();

	return 0;
}
