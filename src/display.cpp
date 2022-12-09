#include "display.h"

#include <functional>

#include "configuration.h"
#include "peripheral.h"

namespace Revolution {
	Display::Display(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const State_space>& state_space,
		const std::reference_wrapper<const Topology>& topology
	) : Peripheral{
		header_space,
		state_space,
		topology,
		topology.get().get_display()
	    } {}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::State_space state_space;
	Revolution::Topology topology;
	Revolution::Display display{header_space, state_space, topology};

	display.main();

	return 0;
}
