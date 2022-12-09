#ifndef REVOLUTION_DISPLAY_H
#define REVOLUTION_DISPLAY_H

#include <functional>

#include "configuration.h"
#include "peripheral.h"

namespace Revolution {
	class Display : public Peripheral {
	public:
		explicit Display(
			const std::reference_wrapper<const Header_space>&
				header_space,
			const std::reference_wrapper<const State_space>&
				state_space,
			const std::reference_wrapper<const Topology>& topology
		);
	};
}

#endif	// REVOLUTION_DISPLAY_H
