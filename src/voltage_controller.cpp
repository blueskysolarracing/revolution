#include <string>

#include "configuration.h"
#include "logger.h"
#include "messenger.h"
#include "voltage_controller.h"
#include "slave.h"

namespace Revolution {
	Voltage_controller::Voltage_controller(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		Logger& logger,
		const Messenger& messenger
	) : Slave{topology, header_space, key_space, logger, messenger}
	{
	}

	const Topology::Endpoint& Voltage_controller::get_endpoint() const
	{
		return get_topology().voltage_controller;
	}
}

int main() {
	Revolution::Topology topology;
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Logger logger{
		Revolution::Logger::Configuration{
			Revolution::Logger::info,
			"./" + topology.voltage_controller.name + ".log"
		}
	};
	Revolution::Messenger messenger{
		Revolution::Messenger::Configuration{
			topology.voltage_controller.name
		},
		logger
	};
	Revolution::Voltage_controller voltage_controller{
		topology,
		header_space,
		key_space,
		logger,
		messenger
	};

	voltage_controller.run();

	return 0;
}
