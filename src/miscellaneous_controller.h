#ifndef REVOLUTION_MISCELLANEOUS_DRIVER_H
#define REVOLUTION_MISCELLANEOUS_DRIVER_H

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	class Miscellaneous_controller : public Soldier {
	public:
		explicit Miscellaneous_controller(
			const Header_space& header_space,
			const Key_space& key_space,
			const Topology& topology
		);
	protected:
		const Topology::Endpoint& get_endpoint() const override;
	};
}

#endif	// REVOLUTION_MISCELLANEOUS_DRIVER_H

