#include "miscellaneous_controller.h"

#include <functional>

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	Miscellaneous_controller::Miscellaneous_controller(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const Key_space>& key_space,
		const std::reference_wrapper<const Topology>& topology
	) : Soldier{header_space, key_space, topology} {}

	const Topology::Endpoint&
		Miscellaneous_controller::get_endpoint() const {
		return get_topology().get_miscellaneous_controller();
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Topology topology;
	Revolution::Miscellaneous_controller miscellaneous_controller{
		header_space,
		key_space,
		topology
	};

	miscellaneous_controller.main();

	return 0;
}

