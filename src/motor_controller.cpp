#include <chrono>

#include "configuration.h"
#include "logger.h"
#include "messenger.h"
#include "motor_controller.h"
#include "slave.h"

namespace Revolution {
	Motor_controller::Motor_controller(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		Logger& logger,
		const Messenger& messenger,
		Heart& heart
	) : Slave{
		topology,
		header_space,
		key_space,
		logger,
		messenger,
		heart
	    }
	{
	}

	const Topology::Endpoint& Motor_controller::get_endpoint() const
	{
		return get_topology().motor_controller;
	}
}

int main() {
	Revolution::Topology topology;
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Logger logger{
		Revolution::Logger::Configuration{
			Revolution::Logger::info,
			"./" + topology.motor_controller.name + ".log"
		}
	};
	Revolution::Messenger messenger{
		Revolution::Messenger::Configuration{
			topology.motor_controller.name
		},
		logger
	};
	Revolution::Heart heart{
		std::chrono::seconds(10),
		[&messenger, &topology, &header_space] () {
			messenger.send(topology.motor_controller.name, header_space.heartbeat);
		},
		logger
	};
	Revolution::Motor_controller motor_controller{
		topology,
		header_space,
		key_space,
		logger,
		messenger,
		heart
	};

	motor_controller.run();

	return 0;
}
