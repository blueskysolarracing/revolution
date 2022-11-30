#include "display.h"

#include <functional>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	Display::Display(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const Key_space>& key_space,
		const std::reference_wrapper<const Topology>& topology
	) : Application{header_space, key_space, topology} {}

	const std::string& Display::get_name() const {
		return get_topology().get_display();
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Topology topology;
	Revolution::Display display{
		header_space,
		key_space,
		topology
	};

	display.main();

	return 0;
}
