#include <chrono>

#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"
#include "soldier.h"
#include "telemeter.h"

namespace Revolution {
	Telemeter::Telemeter(
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

	const Topology::Endpoint& Telemeter::get_endpoint() const
	{
		return get_topology().telemeter;
	}
}

int main() {
	Revolution::Topology topology;
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Logger logger{
		Revolution::Logger::Configuration{
			Revolution::Logger::info,
			"./" + topology.telemeter.name + ".log"
		}
	};
	Revolution::Messenger messenger{
		Revolution::Messenger::Configuration{
			topology.telemeter.name
		},
		logger
	};
	Revolution::Heart heart{
		Revolution::Heart::Configuration{
			std::chrono::seconds(1),
			[&messenger, &topology, &header_space] () {
				messenger.send(
					topology.telemeter.name,
					header_space.heartbeat
				);
			}
		},
		logger
	};
	Revolution::Telemeter telemeter{
		topology,
		header_space,
		key_space,
		logger,
		messenger,
		heart
	};

	telemeter.run();

	return 0;
}
