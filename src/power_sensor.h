#ifndef REVOLUTION_POWER_SENSOR_H
#define REVOLUTION_POWER_SENSOR_H

#include "instance.h"

namespace Revolution {
	class Power_sensor : public Instance {
	public:
		Power_sensor(
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space
		);
	};
}

#endif	// REVOLUTION_POWER_SENSOR_H
