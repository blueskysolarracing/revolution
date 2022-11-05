#include <chrono>

#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"
#include "power_sensor.h"
#include "soldier.h"

namespace Revolution {
	Power_sensor::Power_sensor(
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
			Revolution::Logger::info
		}
	};
	Revolution::Messenger messenger{
		Revolution::Messenger::Configuration{
			topology.power_sensor.name
		},
		logger
	};
	Revolution::Heart heart{
		Revolution::Heart::Configuration{
			std::chrono::seconds(1),
			[&messenger, &topology, &header_space] () {
				messenger.send(
					topology.power_sensor.name,
					header_space.heartbeat
				);
			}
		},
		logger
	};
	Revolution::Power_sensor power_sensor{
		topology,
		header_space,
		key_space,
		logger,
		messenger,
		heart
	};

	power_sensor.run();

	return 0;
}
