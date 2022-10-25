#ifndef REVOLUTION_VOLTAGE_CONTROLLER_H
#define REVOLUTION_VOLTAGE_CONTROLLER_H

#include "instance.h"

namespace Revolution {
	class Voltage_controller : public Instance {
	public:
		Voltage_controller(
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space
		);
	};
}

#endif	// REVOLUTION_VOLTAGE_CONTROLLER_H

