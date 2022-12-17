#ifndef REVOLUTION_HEART_H
#define REVOLUTION_HEART_H

#include <atomic>
#include <chrono>
#include <functional>

namespace Revolution {
    class Heart {
    public:
        void beat();
        void monitor(
            const std::atomic_bool& status,
            const std::chrono::high_resolution_clock::duration& timeout,
            const std::function<void()>& callback
        );
    private:
        std::atomic_uint& get_count();

        std::atomic_uint count;
    };
}

#endif  // REVOLUTION_HEART_H
