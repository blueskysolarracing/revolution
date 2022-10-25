#include "syncer.h"

namespace Revolution {
	Revolution::Syncer::Syncer(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space
	) : Instance{
		topology.syncer.name,
		topology.syncer.logger_configuration,
		topology.syncer.messenger_configuration,
		topology,
		header_space,
		key_space
	    }
	{
	}
}

int main() {
	Revolution::Syncer syncer{
		Revolution::Topology{},
		Revolution::Header_space{},
		Revolution::Key_space{}
	};

	syncer.run();

	return 0;
}

