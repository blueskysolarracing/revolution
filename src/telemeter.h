#ifndef REVOLUTION_TELEMETER_H
#define REVOLUTION_TELEMETER_H

#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"
#include "soldier.h"

namespace Revolution {
	class Telemeter : public Soldier {
	public:
		explicit Telemeter(
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

#endif	// REVOLUTION_TELEMETER_H
