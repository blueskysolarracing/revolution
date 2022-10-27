#include <atomic>
#include <chrono>
#include <functional>
#include <thread>

#include <stdlib.h>

#include "heart.h"
#include "logger.h"

namespace Revolution {
	Heart::Heart(
		const std::chrono::high_resolution_clock::duration& timeout,
		const std::function<void()>& callback,
		Logger& logger
	) : timeout{timeout},
	    callback{callback},
	    logger{logger},
	    thread{&Heart::monitor, this},
	    status{true}
	{
	}

	void Heart::beat()
	{
		get_status().store(true);
	}

	const std::chrono::high_resolution_clock::duration&
		Heart::get_timeout() const
	{
		return timeout;
	}

	const std::function<void()>& Heart::get_callback() const
	{
		return callback;
	}

	Logger& Heart::get_logger() const
	{
		return logger;
	}

	const std::atomic_bool& Heart::get_status() const
	{
		return status;
	}

	std::atomic_bool& Heart::get_status()
	{
		return status;
	}

	void Heart::monitor()
	{
		for (;;) {
			if (!get_status().load()) {
				get_logger() << Logger::fatal
					<< "No heartbeat within the timeout! "
					<< "Heart attack occurred. Crashing..."
					<< std::endl;

				abort();
			}

			get_status().store(false);
			get_callback()();

			std::this_thread::sleep_for(get_timeout());
		}
	}
}
