#ifndef REVOLUTION_MARSHAL_H
#define REVOLUTION_MARSHAL_H

#include "application.h"
#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"

namespace Revolution {
	class Marshal : public Application {
	public:
		explicit Marshal(
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

#endif	// REVOLUTION_MARSHAL_H
