#ifndef REVOLUTION_SYNCER_H
#define REVOLUTION_SYNCER_H

#include "configuration.h"
#include "logger.h"
#include "master.h"
#include "messenger.h"

namespace Revolution {
	class Syncer : public Master {
	public:
		explicit Syncer(
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

#endif	// REVOLUTION_SYNCER_H
