#include "thread_pool.h"

#include <atomic>
#include <condition_variable>
#include <functional>
#include <list>
#include <mutex>
#include <queue>
#include <thread>

namespace Revolution {
    ThreadPool::ThreadPool(const unsigned int& thread_count) : status{true} {
        for (unsigned int i = 0; i < thread_count; ++i)
            threads.emplace_back(std::bind(&ThreadPool::main, this));
    }

    ThreadPool::~ThreadPool() {
        get_status() = false;
        get_condition_variable().notify_all();

        for (auto& thread : get_threads())
            thread.join();
    }

    void ThreadPool::add(const std::function<void()>& function) {
        std::scoped_lock lock{get_mutex()};

        get_functions().push(function);

        get_condition_variable().notify_one();
    }

    const std::atomic_bool& ThreadPool::get_status() const {
        return status;
    }

    const std::list<std::thread>& ThreadPool::get_threads() const {
        return threads;
    }

    const std::queue<std::function<void()>>&
            ThreadPool::get_functions() const {
        return functions;
    }

    const std::mutex& ThreadPool::get_mutex() const {
        return mutex;
    }

    const std::condition_variable&
            ThreadPool::get_condition_variable() const {
        return condition_variable;
    }

    std::atomic_bool& ThreadPool::get_status() {
        return status;
    }

    std::list<std::thread>& ThreadPool::get_threads() {
        return threads;
    }

    std::queue<std::function<void()>>& ThreadPool::get_functions() {
        return functions;
    }

    std::mutex& ThreadPool::get_mutex() {
        return mutex;
    }

    std::condition_variable& ThreadPool::get_condition_variable() {
        return condition_variable;
    }

    void ThreadPool::main() {
        while (get_status()) {
            std::function<void()> function;

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
