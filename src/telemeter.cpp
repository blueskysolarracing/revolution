#include "telemeter.h"

namespace Revolution {
	Revolution::Telemeter::Telemeter(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space
	) : Instance{
		topology.telemeter.name,
		topology.telemeter.logger_configuration,
		topology.telemeter.messenger_configuration,
		topology,
		header_space,
		key_space
	    }
	{
	}
}

int main() {
	Revolution::Telemeter telemeter{
		Revolution::Topology{},
		Revolution::Header_space{},
		Revolution::Key_space{}
	};

	telemeter.run();

	return 0;
}

