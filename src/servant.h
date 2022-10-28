#ifndef REVOLUTION_SERVANT_H
#define REVOLUTION_SERVANT_H

#include "application.h"
#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"

namespace Revolution {
	class Servant : public Application {
	public:
		explicit Servant(
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space,
			Logger& logger,
			const Messenger& messenger,
			Heart& heart
		);

		void run() override;
	protected:
		void handle_set(const Messenger::Message& message) override;
	};
}

#endif	// REVOLUTION_SERVANT_H
