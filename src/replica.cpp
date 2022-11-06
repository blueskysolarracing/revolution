#include <chrono>

#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"
#include "replica.h"
#include "soldier.h"

namespace Revolution {
	Replica::Replica(
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

	const Topology::Endpoint& Replica::get_endpoint() const
	{
		return get_topology().replica;
	}
}

int main() {
	Revolution::Topology topology;
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Logger logger{Revolution::Logger::Configuration{}};
	Revolution::Messenger messenger{
		Revolution::Messenger::Configuration{
			topology.replica.name
		},
		logger
	};
	Revolution::Heart heart{
		Revolution::Heart::Configuration{
			std::chrono::seconds(1),
			[&messenger, &topology, &header_space] () {
				messenger.send(
					topology.replica.name,
					header_space.heartbeat
				);
			}
		},
		logger
	};
	Revolution::Replica replica{
		topology,
		header_space,
		key_space,
		logger,
		messenger,
		heart
	};

	replica.run();

	return 0;
}
