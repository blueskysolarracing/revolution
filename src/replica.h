#ifndef REVOLUTION_REPLICA_H
#define REVOLUTION_REPLICA_H

#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"
#include "soldier.h"

namespace Revolution {
	class Replica : public Soldier {
	public:
		explicit Replica(
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

#endif	// REVOLUTION_REPLICA_H
