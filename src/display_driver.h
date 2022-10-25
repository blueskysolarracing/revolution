#ifndef REVOLUTION_DISPLAY_DRIVER_H
#define REVOLUTION_DISPLAY_DRIVER_H

#include "instance.h"

namespace Revolution {
	class Display_driver : public Instance {
	public:
		Display_driver(
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space
		);
	};
}

#endif	// REVOLUTION_DISPLAY_DRIVER_H
