#include <atomic>
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <thread>

#include "heart.h"
#include "logger.h"

namespace Revolution {
	Heart::Heart(const Timeout& timeout)
		: timeout{timeout},
		  thread{&Heart::monitor, this},
		  status{true},
		  count{1} {}

	Heart::~Heart() {
		get_status() = false;
		get_thread().join();
	}

	void Heart::beat() {
		++get_count();
	}

	const Heart::Timeout Heart::default_timeout
		= std::chrono::seconds(1);

	const Heart::Timeout& Heart::get_default_timeout() {
		return default_timeout;
	}

	const Heart::Timeout& Heart::get_timeout() const {
		return timeout;
	}

	const std::thread& Heart::get_thread() const {
		return thread;
	}

	const std::atomic_bool& Heart::get_status() const {
		return status;
	}

	const std::atomic_uint& Heart::get_count() const {
		return count;
	}

	std::thread& Heart::get_thread() {
		return thread;
	}

	std::atomic_bool& Heart::get_status() {
		return status;
	}

	std::atomic_uint& Heart::get_count() {
		return count;
	}

	void Heart::monitor() {
		while (get_status()) {
			if (!get_count()) {
				std::cerr << "No heartbeat within the timeout! "
					<< "Heart attack occurred. Aborting..."
					<< std::endl;

				std::abort();
			}

			get_count() = 0;

			std::this_thread::sleep_for(get_timeout());
		}
	}
}
