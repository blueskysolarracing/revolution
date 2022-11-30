#include "hardware.h"

#include <functional>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	Hardware::Hardware(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const Key_space>& key_space,
		const std::reference_wrapper<const Topology>& topology
	) : Application{header_space, key_space, topology} {}

	const std::string& Hardware::get_name() const {
		return get_topology().get_hardware();
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Topology topology;
	Revolution::Hardware hardware{
		header_space,
		key_space,
		topology
	};

	hardware.main();

	return 0;
}

