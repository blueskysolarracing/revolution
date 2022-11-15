#ifndef REVOLUTION_WORKER_POOL_H
#define REVOLUTION_WORKER_POOL_H

#include <atomic>
#include <condition_variable>
#include <functional>
#include <list>
#include <mutex>
#include <queue>
#include <thread>

namespace Revolution {
	class Worker_pool {
	public:
		using Job = std::function<void()>;

		Worker_pool();
		~Worker_pool();

		void work(const Job& job);
	private:
		static const unsigned int thread_count;

		static const unsigned int& get_thread_count();

		const std::atomic_bool& get_status() const;
		const std::list<std::thread>& get_threads() const;
		const std::queue<Job>& get_jobs() const;
		const std::mutex& get_job_mutex() const;
		const std::condition_variable& get_job_condition_variable() const;

		std::atomic_bool& get_status();
		std::list<std::thread>& get_threads();
		std::queue<Job>& get_jobs();
		std::mutex& get_job_mutex();
		std::condition_variable& get_job_condition_variable();

		void worker();

		std::atomic_bool status;
		std::list<std::thread> threads;
		std::queue<Job> jobs;
		std::mutex job_mutex;
		std::condition_variable job_condition_variable;
	};
}

#endif  // REVOLUTION_WORKER_POOL_H
