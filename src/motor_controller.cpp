#include "motor_controller.h"

#include <functional>

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	Motor_controller::Motor_controller(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const Key_space>& key_space,
		const std::reference_wrapper<const Topology>& topology
	) : Soldier{header_space, key_space, topology} {}

	const Topology::Endpoint& Motor_controller::get_endpoint() const {
		return get_topology().get_motor_controller();
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Topology topology;
	Revolution::Motor_controller motor_controller{
		header_space,
		key_space,
		topology
	};

	motor_controller.main();

	return 0;
}

