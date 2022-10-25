#include "power_sensor.h"

namespace Revolution {
	Revolution::Power_sensor::Power_sensor(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space
	) : Instance{
		topology.power_sensor.name,
		topology.power_sensor.logger_configuration,
		topology.power_sensor.messenger_configuration,
		topology,
		header_space,
		key_space
	    }
	{
	}
}

int main() {
	Revolution::Power_sensor power_sensor{
		Revolution::Topology{},
		Revolution::Header_space{},
		Revolution::Key_space{}
	};

	power_sensor.run();

	return 0;
}

