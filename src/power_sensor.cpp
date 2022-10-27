#include "configuration.h"
#include "logger.h"
#include "messenger.h"
#include "power_sensor.h"
#include "slave.h"

namespace Revolution {
	Power_sensor::Power_sensor(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		Logger& logger,
		const Messenger& messenger
	) : Slave{topology, header_space, key_space, logger, messenger}
	{
	}

	const Topology::Endpoint& Power_sensor::get_endpoint() const
	{
		return get_topology().power_sensor;
	}
}

int main() {
	Revolution::Topology topology;
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Logger logger{
		Revolution::Logger::Configuration{
			Revolution::Logger::info,
			"./" + topology.power_sensor.name + ".log"
		}
	};
	Revolution::Messenger messenger{
		Revolution::Messenger::Configuration{
			topology.power_sensor.name
		},
		logger
	};
	Revolution::Power_sensor power_sensor{
		topology,
		header_space,
		key_space,
		logger,
		messenger
	};

	power_sensor.run();

	return 0;
}
