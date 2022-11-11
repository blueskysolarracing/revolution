#ifndef REVOLUTION_POWER_SENSOR_H
#define REVOLUTION_POWER_SENSOR_H

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	class Power_sensor : public Soldier {
	public:
		explicit Power_sensor(
			const Header_space& header_space,
			const Key_space& key_space,
			const Topology& topology
		);
	protected:
		const Topology::Endpoint& get_endpoint() const override;
	};
}

#endif	// REVOLUTION_POWER_SENSOR_H

