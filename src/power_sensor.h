#ifndef REVOLUTION_POWER_SENSOR_H
#define REVOLUTION_POWER_SENSOR_H

#include "configuration.h"
#include "logger.h"
#include "messenger.h"
#include "slave.h"

namespace Revolution {
	class Power_sensor : public Slave {
	public:
		explicit Power_sensor(
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

#endif	// REVOLUTION_POWER_SENSOR_H
