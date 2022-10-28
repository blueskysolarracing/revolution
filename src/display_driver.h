#ifndef REVOLUTION_DISPLAY_DRIVER_H
#define REVOLUTION_DISPLAY_DRIVER_H

#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"
#include "servant.h"

namespace Revolution {
	class Display_driver : public Servant {
	public:
		explicit Display_driver(
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space,
			Logger& logger,
			const Messenger& messenger,
			Heart& heart
		);
	protected:
		const Topology::Endpoint& get_endpoint() const override;
	};
}

#endif	// REVOLUTION_DISPLAY_DRIVER_H
