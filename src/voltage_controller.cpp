#include <chrono>

#include "configuration.h"
#include "logger.h"
#include "messenger.h"
#include "slave.h"
#include "voltage_controller.h"

namespace Revolution {
	Voltage_controller::Voltage_controller(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		Logger& logger,
		const Messenger& messenger,
		Heart& heart
	) : Slave{
		topology,
		header_space,
		key_space,
		logger,
		messenger,
		heart
	    }
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
	Revolution::Heart heart{
		std::chrono::seconds(10),
		[&messenger, &topology, &header_space] () {
			messenger.send(topology.voltage_controller.name, header_space.heartbeat);
		},
		logger
	};
	Revolution::Voltage_controller voltage_controller{
		topology,
		header_space,
		key_space,
		logger,
		messenger,
		heart
	};

	voltage_controller.run();

	return 0;
}
