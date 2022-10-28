#ifndef REVOLUTION_HEART_H
#define REVOLUTION_HEART_H

#include <atomic>
#include <chrono>
#include <functional>
#include <thread>

#include "logger.h"

namespace Revolution {
	class Heart {
	public:
		explicit Heart(
			const std::chrono::high_resolution_clock::duration& timeout,
			const std::function<void()>& callback,
			Logger& logger
		);
		~Heart();

		void beat();
	private:
		const std::chrono::high_resolution_clock::duration& get_timeout() const;
		const std::function<void()>& get_callback() const;
		Logger& get_logger() const;
		const std::atomic_bool& get_status() const;
		std::atomic_bool& get_status();
		const std::atomic_uint& get_count() const;
		std::atomic_uint& get_count();

		void monitor();

		const std::chrono::high_resolution_clock::duration timeout;
		const std::function<void()> callback;
		Logger& logger;
		std::thread thread;
		std::atomic_bool status;
		std::atomic_uint count;
	};
}

#endif	// REVOLUTION_HEART_H
