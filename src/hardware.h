#ifndef REVOLUTION_HARDWARE_H
#define REVOLUTION_HARDWARE_H

#include <functional>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	class Hardware : public Application {
	public:
		explicit Hardware(
			const std::reference_wrapper<const Header_space>&
				header_space,
			const std::reference_wrapper<const Key_space>&
				key_space,
			const std::reference_wrapper<const Topology>& topology
		);
	};
}

#endif	// REVOLUTION_HARDWARE_H
