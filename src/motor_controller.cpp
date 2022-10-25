#include "motor_controller.h"

namespace Revolution {
	Revolution::Motor_controller::Motor_controller(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space
	) : Instance{
		topology.motor_controller.name,
		topology.motor_controller.logger_configuration,
		topology.motor_controller.messenger_configuration,
		topology,
		header_space,
		key_space
	    }
	{
	}
}

int main() {
	Revolution::Motor_controller motor_controller{
		Revolution::Topology{},
		Revolution::Header_space{},
		Revolution::Key_space{}
	};

	motor_controller.run();

	return 0;
}
