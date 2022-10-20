#ifndef REVOLUTION_TOPOLOGY_H_
#define REVOLUTION_TOPOLOGY_H_

#include <iostream>
#include <vector>
#include <string>

namespace revolution {
struct Instance {
	const std::string name;
};
struct Topology {

	static Instance master;
	static std::vector<Instance> slaves;
	static Instance null;

	static const Instance &getInstance(const std::string &name) {
		if (master.name == name)
			return master;

		for (const auto &slave : slaves)
			if (slave.name == name)
				return slave;

		std::cout << "ERROR instance not found" << std::endl;

		return null;
	}
};
}

#endif  // REVOLUTION_TOPOLOGY_H_
