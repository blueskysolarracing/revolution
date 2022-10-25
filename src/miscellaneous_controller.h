#ifndef REVOLUTION_MISCELLANEOUS_CONTROLLER_H
#define REVOLUTION_MISCELLANEOUS_CONTROLLER_H

#include "instance.h"

namespace Revolution {
	class Miscellaneous_controller : public Instance {
	public:
		Miscellaneous_controller(
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space
		);
	};
}

#endif	// REVOLUTION_MISCELLANEOUS_CONTROLLER_H
