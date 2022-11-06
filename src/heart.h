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
		struct Configuration {
			explicit Configuration(
				const std::chrono::high_resolution_clock::duration&
					timeout,
				const std::function<void()>& callback
			);

			const std::chrono::high_resolution_clock::duration timeout;
			const std::function<void()> callback;
		};

		explicit Heart(
			const Configuration& configuration,
			const Logger& logger
		);
		~Heart();

		void beat();
	private:
		const Configuration& get_configuration() const;
		const Logger& get_logger() const;
		const std::atomic_bool& get_status() const;
		std::atomic_bool& get_status();
		const std::atomic_uint& get_count() const;
		std::atomic_uint& get_count();

		void monitor();

		const Configuration configuration;
		const Logger& logger;
		std::thread thread;
		std::atomic_bool status;
		std::atomic_uint count;
	};
}

#endif	// REVOLUTION_HEART_H
