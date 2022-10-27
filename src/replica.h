#ifndef REVOLUTION_WATCHDOG_H
#define REVOLUTION_WATCHDOG_H

#include "instance.h"

namespace Revolution {
	class Watchdog : public Instance {
	public:
		Watchdog(
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space
		);

		void run() override;
	protected:
		void update(const std::optional<Messenger::Message>& optional_message) override;
		bool is_running(const Topology::Endpoint& endpoint);
		void start(const Topology::Endpoint& endpoint);
		void stop(const Topology::Endpoint& endpoint);
	};
}

#endif	// REVOLUTION_WATCHDOG_H

