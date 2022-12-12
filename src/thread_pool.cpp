#include "thread_pool.h"

#include <atomic>
#include <condition_variable>
#include <functional>
#include <list>
#include <mutex>
#include <queue>
#include <thread>

namespace Revolution {
	Thread_pool::Thread_pool(const unsigned int& thread_count)
		: status{true},
		  threads{},
		  functions{},
		  mutex{},
		  condition_variable{} {
		for (unsigned int i = 0; i < thread_count; ++i)
			threads.emplace_back(
				std::bind(&Thread_pool::main, this)
			);
	}

	Thread_pool::~Thread_pool() {
		get_status() = false;
		get_condition_variable().notify_all();

		for (auto& thread : get_threads())
			thread.join();
	}

	void Thread_pool::add(const std::function<void()>& function) {
		std::unique_lock lock{get_mutex()};

		get_functions().push(function);

		get_condition_variable().notify_one();
	}

	const std::atomic_bool& Thread_pool::get_status() const {
		return status;
	}

	const std::list<std::thread>& Thread_pool::get_threads() const {
		return threads;
	}

	const std::queue<std::function<void()>>& Thread_pool::get_functions() const {
		return functions;
	}

	const std::mutex& Thread_pool::get_mutex() const {
		return mutex;
	}

	const std::condition_variable&
		Thread_pool::get_condition_variable() const {
		return condition_variable;
	}

	std::atomic_bool& Thread_pool::get_status() {
		return status;
	}

	std::list<std::thread>& Thread_pool::get_threads() {
		return threads;
	}

	std::queue<std::function<void()>>& Thread_pool::get_functions() {
		return functions;
	}

	std::mutex& Thread_pool::get_mutex() {
		return mutex;
	}

	std::condition_variable& Thread_pool::get_condition_variable() {
		return condition_variable;
	}

	void Thread_pool::main() {
		while (get_status()) {
			std::function<void()> function{};

			{
				std::unique_lock lock{get_mutex()};

				while (get_functions().empty() && get_status())
					get_condition_variable().wait(lock);

				if (!get_functions().empty()) {
					function = get_functions().front();
					get_functions().pop();
				}
			}

			if (function)
				function();
		}
	}
}
