#include <string>

#include "configuration.h"
#include "logger.h"
#include "master.h"
#include "messenger.h"
#include "syncer.h"

namespace Revolution {
	Syncer::Syncer(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		Logger& logger,
		const Messenger& messenger
	) : Master{topology, header_space, key_space, logger, messenger}
	{
	}

	const Topology::Endpoint& Syncer::get_endpoint() const
	{
		return get_topology().syncer;
	}
}

int main() {
	Revolution::Topology topology;
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Logger logger{
		Revolution::Logger::Configuration{
			Revolution::Logger::info,
			"./" + topology.syncer.name + ".log"
		}
	};
	Revolution::Messenger messenger{
		Revolution::Messenger::Configuration{
			topology.syncer.name
		},
		logger
	};
	Revolution::Syncer syncer{
		topology,
		header_space,
		key_space,
		logger,
		messenger
	};

	syncer.run();

	return 0;
}
