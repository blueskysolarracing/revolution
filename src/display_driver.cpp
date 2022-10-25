#include "display_driver.h"

namespace Revolution {
	Revolution::Display_driver::Display_driver(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space
	) : Instance{
		topology.display_driver.name,
		topology.display_driver.logger_configuration,
		topology.display_driver.messenger_configuration,
		topology,
		header_space,
		key_space
	    }
	{
	}
}

int main() {
	Revolution::Display_driver display_driver{
		Revolution::Topology{},
		Revolution::Header_space{},
		Revolution::Key_space{}
	};

	display_driver.run();

	return 0;
}
