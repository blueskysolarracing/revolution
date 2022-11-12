#include "telemeter.h"

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	Telemeter::Telemeter(
		const Header_space& header_space,
		const Key_space& key_space,
		const Topology& topology
	) : Soldier{header_space, key_space, topology} {}

	const Topology::Endpoint& Telemeter::get_endpoint() const {
		return get_topology().get_telemeter();
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Topology topology;
	Revolution::Telemeter telemeter{header_space, key_space, topology};

	telemeter.run();

	return 0;
}

