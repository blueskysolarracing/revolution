#include "configuration.h"
#include "logger.h"
#include "messenger.h"
#include "slave.h"
#include "telemeter.h"

namespace Revolution {
	Telemeter::Telemeter(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		Logger& logger,
		const Messenger& messenger
	) : Slave{topology, header_space, key_space, logger, messenger}
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
	Revolution::Telemeter telemeter{
		topology,
		header_space,
		key_space,
		logger,
		messenger
	};

	telemeter.run();

	return 0;
}
