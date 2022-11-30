#ifndef REVOLUTION_HEART_H
#define REVOLUTION_HEART_H

#include <atomic>
#include <chrono>
#include <thread>

namespace Revolution {
	class Heart {
	public:
		using Timeout = std::chrono::high_resolution_clock::duration;

		explicit Heart(const Timeout& timeout = get_default_timeout());
		~Heart();

		void beat();
	private:
		static const Timeout default_timeout;

		static const Timeout& get_default_timeout();

		const Timeout& get_timeout() const;
		const std::thread& get_thread() const;
		const std::atomic_bool& get_status() const;
		const std::atomic_uint& get_count() const;

		std::thread& get_thread();
		std::atomic_bool& get_status();
		std::atomic_uint& get_count();

		void monitor();

		const Timeout timeout;
		std::thread thread;
		std::atomic_bool status;
		std::atomic_uint count;
	};
}

#endif	// REVOLUTION_HEART_H
