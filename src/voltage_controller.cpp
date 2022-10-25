#include "voltage_controller.h"

namespace Revolution {
	Revolution::Voltage_controller::Voltage_controller(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space
	) : Instance{
		topology.voltage_controller.name,
		topology.voltage_controller.logger_configuration,
		topology.voltage_controller.messenger_configuration,
		topology,
		header_space,
		key_space
	    }
	{
	}
}

int main() {
	Revolution::Voltage_controller voltage_controller{
		Revolution::Topology{},
		Revolution::Header_space{},
		Revolution::Key_space{}
	};

	voltage_controller.run();

	return 0;
}
