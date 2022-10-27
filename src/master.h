#ifndef REVOLUTION_MASTER_H
#define REVOLUTION_MASTER_H

#include <chrono>

#include "application.h"
#include "configuration.h"
#include "logger.h"
#include "messenger.h"

namespace Revolution {
	class Master : public Application {
	public:
		explicit Master(
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space,
			Logger& logger,
			const Messenger& messenger,
			const std::chrono::high_resolution_clock::duration&
				failover_timeout
		);

		void run() override;
	protected:
		void handle_set(const Messenger::Message& message) override;
	private:
		const std::chrono::high_resolution_clock::duration&
			get_failover_timeout() const;

		const std::chrono::high_resolution_clock::duration&
			failover_timeout;
	};
}

#endif	// REVOLUTION_MASTER_H
