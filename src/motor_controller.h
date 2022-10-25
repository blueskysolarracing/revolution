#ifndef REVOLUTION_MOTOR_CONTROLLER_H
#define REVOLUTION_MOTOR_CONTROLLER_H

#include "instance.h"

namespace Revolution {
	class Motor_controller : public Instance {
	public:
		Motor_controller(
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space
		);
	};
}

#endif	// REVOLUTION_MOTOR_CONTROLLER_H
