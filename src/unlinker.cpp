#include <string>
#include <vector>

#include <mqueue.h>

#include "configuration.h"

int main(int argc, char *argv[]) {
	std::vector<std::string> names;

	if (argc > 1)
		for (int i = 0; i < argc; ++i)
			names.emplace_back(argv[i]);
	else {
		Revolution::Topology topology;

		for (const auto& endpoint : topology.get_endpoints())
			names.push_back(endpoint.get().get_name());
	}

	for (const auto& name : names)
		mq_unlink(('/' + name).data());

	return 0;
}
