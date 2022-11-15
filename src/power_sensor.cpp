#include "power_sensor.h"

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	Power_sensor::Power_sensor(
		const Header_space& header_space,
		const Key_space& key_space,
		const Topology& topology
	) : Soldier{header_space, key_space, topology} {}

	const Topology::Endpoint& Power_sensor::get_endpoint() const {
		return get_topology().get_power_sensor();
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Topology topology;
	Revolution::Power_sensor power_sensor{
		header_space,
		key_space,
		topology
	};

	power_sensor.main();

	return 0;
}

