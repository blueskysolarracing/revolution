#include "voltage_controller.h"

#include <functional>

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	Voltage_controller::Voltage_controller(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const Key_space>& key_space,
		const std::reference_wrapper<const Topology>& topology
	) : Soldier{header_space, key_space, topology} {}

	const Topology::Endpoint& Voltage_controller::get_endpoint() const {
		return get_topology().get_voltage_controller();
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Topology topology;
	Revolution::Voltage_controller voltage_controller{
		header_space,
		key_space,
		topology
	};

	voltage_controller.main();

	return 0;
}

