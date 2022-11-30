#ifndef REVOLUTION_DISPLAY_H
#define REVOLUTION_DISPLAY_H

#include <functional>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	class Display : public Application {
	public:
		explicit Display(
			const std::reference_wrapper<const Header_space>&
				header_space,
			const std::reference_wrapper<const Key_space>&
				key_space,
			const std::reference_wrapper<const Topology>& topology
		);
	};
}

#endif	// REVOLUTION_DISPLAY_H
