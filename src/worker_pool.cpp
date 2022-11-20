#include "worker_pool.h"

#include <atomic>
#include <condition_variable>
#include <functional>
#include <list>
#include <mutex>
#include <queue>
#include <thread>

namespace Revolution {
	Worker_pool::Worker_pool(const unsigned int& thread_count)
		: status{true},
		  threads{},
	    	  jobs{},
	    	  job_mutex{},
	    	  job_condition_variable{} {
		for (unsigned int i = 0; i < thread_count; ++i)
			threads.emplace_back(
				std::bind(&Worker_pool::worker, this)
			);
	}

	Worker_pool::~Worker_pool() {
		get_status() = false;
		get_job_condition_variable().notify_all();

		for (auto& thread : get_threads())
			thread.join();
	}

	void Worker_pool::work(const Job& job) {
		std::unique_lock lock{get_job_mutex()};

		get_jobs().emplace(job);

		get_job_condition_variable().notify_one();
	}

	const unsigned int Worker_pool::default_thread_count{
		std::thread::hardware_concurrency()
	};

	const unsigned int& Worker_pool::get_default_thread_count() {
		return default_thread_count;
	}

	const std::atomic_bool& Worker_pool::get_status() const {
		return status;
	}

	const std::list<std::thread>& Worker_pool::get_threads() const {
		return threads;
	}

	const std::queue<Worker_pool::Job>& Worker_pool::get_jobs() const {
		return jobs;
	}

	const std::mutex& Worker_pool::get_job_mutex() const {
		return job_mutex;
	}

	const std::condition_variable&
		Worker_pool::get_job_condition_variable() const {
		return job_condition_variable;
	}

	std::atomic_bool& Worker_pool::get_status() {
		return status;
	}

	std::list<std::thread>& Worker_pool::get_threads() {
		return threads;
	}

	std::queue<Worker_pool::Job>& Worker_pool::get_jobs() {
		return jobs;
	}

	std::mutex& Worker_pool::get_job_mutex() {
		return job_mutex;
	}
	
	std::condition_variable& Worker_pool::get_job_condition_variable() {
		return job_condition_variable;
	}
	
	void Worker_pool::worker() {
		while (get_status()) {
			Job job = nullptr;

			{
				std::unique_lock lock{get_job_mutex()};

				while (get_jobs().empty() && get_status())
					get_job_condition_variable().wait(lock);

				if (!get_jobs().empty()) {
					job = get_jobs().front();
					get_jobs().pop();
				}
			}

			if (job)
				job();
		}
	}
}
