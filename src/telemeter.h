#ifndef REVOLUTION_TELEMETER_H
#define REVOLUTION_TELEMETER_H

#include "instance.h"

namespace Revolution {
	class Telemeter : public Instance {
	public:
		Telemeter(
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space
		);
	};
}

#endif	// REVOLUTION_TELEMETER_H
