#ifndef REVOLUTION_TOPOLOGY_H_
#define REVOLUTION_TOPOLOGY_H_

#include <unordered_map>

namespace revolution {
struct Topology {
	static struct Instance {
		const std::string name;
	}

	static const Instance master;
	static const std::vector<Instance> slaves;
	static const Instance null;

	static const Instance &getInstance(const std::string &name) {
		if (master.name == name)
			return master

		for (const auto &slave : slaves)
			if (slave.name == name)
				return slave

		std::cout << "ERROR instance not found" << std::endl;

		return null;
	}
}
}

#endif  // REVOLUTION_TOPOLOGY_H_
