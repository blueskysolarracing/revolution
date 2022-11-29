#ifndef REVOLUTION_POWER_SENSOR_H
#define REVOLUTION_POWER_SENSOR_H

#include <functional>

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	class Power_sensor : public Soldier {
	public:
		explicit Power_sensor(
			const std::reference_wrapper<const Header_space>&
				header_space,
			const std::reference_wrapper<const Key_space>&
				key_space,
			const std::reference_wrapper<const Topology>& topology
		);
	protected:
		const Topology::Endpoint& get_endpoint() const override;
	};
}

#endif	// REVOLUTION_POWER_SENSOR_H

