#ifndef REVOLUTION_MOTOR_CONTROLLER_H
#define REVOLUTION_MOTOR_CONTROLLER_H

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	class Motor_controller : public Soldier {
	public:
		explicit Motor_controller(
			const Header_space& header_space,
			const Key_space& key_space,
			const Topology& topology
		);
	protected:
		const Topology::Endpoint& get_endpoint() const override;
	};
}

#endif	// REVOLUTION_MOTOR_CONTROLLER_H

