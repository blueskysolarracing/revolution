#include <mqueue.h>

#include "configuration.h"

int main() {
	Revolution::Topology topology;

	for (const auto& endpoint : topology.get_endpoints())
		mq_unlink(('/' + endpoint.get().get_name()).data());

	return 0;
}
