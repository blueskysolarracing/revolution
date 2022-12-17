#ifndef REVOLUTION_THREAD_POOL_H
#define REVOLUTION_THREAD_POOL_H

#include <atomic>
#include <condition_variable>
#include <functional>
#include <list>
#include <mutex>
#include <queue>
#include <thread>

namespace Revolution {
    class ThreadPool {
    public:
        explicit ThreadPool(const unsigned int& thread_count);
        ~ThreadPool();

        void add(const std::function<void()>& function);
    private:
        const std::atomic_bool& get_status() const;
        const std::list<std::thread>& get_threads() const;
        const std::queue<std::function<void()>>& get_functions() const;
        const std::mutex& get_mutex() const;
        const std::condition_variable& get_condition_variable() const;

        std::atomic_bool& get_status();
        std::list<std::thread>& get_threads();
        std::queue<std::function<void()>>& get_functions();
        std::mutex& get_mutex();
        std::condition_variable& get_condition_variable();

        void main();

        std::atomic_bool status;
        std::list<std::thread> threads;
        std::queue<std::function<void()>> functions;
        std::mutex mutex;
        std::condition_variable condition_variable;
    };
}

#endif  // REVOLUTION_THREAD_POOL_H
