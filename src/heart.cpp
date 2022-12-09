#include "heart.h"

#include <atomic>
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <thread>

namespace Revolution {
	Heart::Heart(const Timeout& beat_timeout)
		: beat_timeout{beat_timeout},
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

	const Heart::Timeout Heart::default_beat_timeout{
		std::chrono::seconds(5)
	};

	const Heart::Timeout& Heart::get_default_beat_timeout() {
		return default_beat_timeout;
	}

	const Heart::Timeout& Heart::get_beat_timeout() const {
		return beat_timeout;
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

			std::this_thread::sleep_for(get_beat_timeout());
		}
	}
}
