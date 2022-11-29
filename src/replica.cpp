#include "replica.h"

#include <functional>

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	Replica::Replica(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const Key_space>& key_space,
		const std::reference_wrapper<const Topology>& topology
	) : Soldier{header_space, key_space, topology} {}

	const Topology::Endpoint& Replica::get_endpoint() const {
		return get_topology().get_replica();
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Topology topology;
	Revolution::Replica replica{header_space, key_space, topology};

	replica.main();

	return 0;
}

