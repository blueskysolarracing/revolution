#include "display_driver.h"

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	Display_driver::Display_driver(
		const Header_space& header_space,
		const Key_space& key_space,
		const Topology& topology
	) : Soldier{header_space, key_space, topology} {}

	const Topology::Endpoint& Display_driver::get_endpoint() const {
		return get_topology().get_display_driver();
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Topology topology;
	Revolution::Display_driver display_driver{
		header_space,
		key_space,
		topology,
	};

	display_driver.run();

	return 0;
}
