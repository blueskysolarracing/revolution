#ifndef REVOLUTION_SLAVE_H
#define REVOLUTION_SLAVE_H

#include "application.h"
#include "configuration.h"
#include "logger.h"
#include "messenger.h"

namespace Revolution {
	class Slave : public Application {
	public:
		explicit Slave(
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space,
			Logger& logger,
			const Messenger& messenger
		);

		void run() override;
	protected:
		void handle_set(const Messenger::Message& message) override;
	};
}

#endif	// REVOLUTION_SLAVE_H
