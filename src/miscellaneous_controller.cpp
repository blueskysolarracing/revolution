#include "miscellaneous_controller.h"

namespace Revolution {
	Revolution::Miscellaneous_controller::Miscellaneous_controller(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space
	) : Instance{
		topology.miscellaneous_controller.name,
		topology.miscellaneous_controller.logger_configuration,
		topology.miscellaneous_controller.messenger_configuration,
		topology,
		header_space,
		key_space
	    }
	{
	}
}

int main() {
	Revolution::Miscellaneous_controller miscellaneous_controller{
		Revolution::Topology{},
		Revolution::Header_space{},
		Revolution::Key_space{}
	};

	miscellaneous_controller.run();

	return 0;
}
