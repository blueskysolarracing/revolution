#ifndef REVOLUTION_Replica_H
#define REVOLUTION_Replica_H

#include "configuration.h"
#include "logger.h"
#include "messenger.h"
#include "slave.h"

namespace Revolution {
	class Replica : public Slave {
	public:
		explicit Replica(
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

#endif	// REVOLUTION_Replica_H
