#ifndef REVOLUTION_SYNCER_H
#define REVOLUTION_SYNCER_H

#include "instance.h"

namespace Revolution {
	class Syncer : public Instance {
	public:
		Syncer(
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space
		);
	};
}

#endif	// REVOLUTION_SYNCER_H
