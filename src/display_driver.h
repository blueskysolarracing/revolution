#ifndef REVOLUTION_DISPLAY_DRIVER_H
#define REVOLUTION_DISPLAY_DRIVER_H

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	class Display_driver : public Soldier {
	public:
		explicit Display_driver(
			const Header_space& header_space,
			const Key_space& key_space,
			const Topology& topology
		);
	protected:
		const Topology::Endpoint& get_endpoint() const override;
	};
}

#endif	// REVOLUTION_DISPLAY_DRIVER_H
