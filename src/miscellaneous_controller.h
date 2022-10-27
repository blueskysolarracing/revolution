#ifndef REVOLUTION_MISCELLANEOUS_CONTROLLER_H
#define REVOLUTION_MISCELLANEOUS_CONTROLLER_H

#include "configuration.h"
#include "logger.h"
#include "messenger.h"
#include "slave.h"

namespace Revolution {
	class Miscellaneous_controller : public Slave {
	public:
		explicit Miscellaneous_controller(
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

#endif	// REVOLUTION_MISCELLANEOUS_CONTROLLER_H
