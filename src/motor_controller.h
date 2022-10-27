#ifndef REVOLUTION_MOTOR_CONTROLLER_H
#define REVOLUTION_MOTOR_CONTROLLER_H

#include "configuration.h"
#include "logger.h"
#include "messenger.h"
#include "slave.h"

namespace Revolution {
	class Motor_controller : public Slave {
	public:
		explicit Motor_controller(
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space,
			Logger& logger,
			const Messenger& messenger
		);
	protected:
		const Topology::Endpoint& get_endpoint() const override;
	};
}

#endif	// REVOLUTION_MOTOR_CONTROLLER_H
