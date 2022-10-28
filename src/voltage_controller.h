#ifndef REVOLUTION_VOLTAGE_CONTROLLER_H
#define REVOLUTION_VOLTAGE_CONTROLLER_H

#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"
#include "servant.h"

namespace Revolution {
	class Voltage_controller : public Servant {
	public:
		explicit Voltage_controller(
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

#endif	// REVOLUTION_VOLTAGE_CONTROLLER_H
