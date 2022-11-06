#include <atomic>
#include <chrono>
#include <functional>
#include <thread>

#include <stdlib.h>

#include "heart.h"
#include "logger.h"

namespace Revolution {
	Heart::Configuration::Configuration(
		const std::chrono::high_resolution_clock::duration& timeout,
		const std::function<void()>& callback
	) : timeout{timeout}, callback{callback}
	{
	}

	Heart::Heart(const Configuration& configuration, const Logger& logger)
		: configuration{configuration},
		  logger{logger},
		  thread{&Heart::monitor, this},
		  status{true},
		  count{1}
	{
	}

	Heart::~Heart()
	{
		status.store(false);
		thread.join();
	}

	void Heart::beat()
	{
		++get_count();
	}

	const Heart::Configuration& Heart::get_configuration() const
	{
		return configuration;
	}

	const Logger& Heart::get_logger() const
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

	const std::atomic_uint& Heart::get_count() const
	{
		return count;
	}

	std::atomic_uint& Heart::get_count()
	{
		return count;
	}

	void Heart::monitor()
	{
		while (get_status().load()) {
			if (!get_count().load()) {
				get_logger() << Logger::alert
					<< "No heartbeat within the timeout! "
					<< "Heart attack occurred. Aborting..."
					<< std::endl;

				abort();
			}

			get_count().store(0);
			get_configuration().callback();

			std::this_thread::sleep_for(get_configuration().timeout);
		}
	}
}
