#ifndef REVOLUTION_HEART_H
#define REVOLUTION_HEART_H

#include <atomic>
#include <chrono>

namespace Revolution {
    class Heart {
    public:
        explicit Heart();

        const std::atomic_uint& get_count() const;

        void beat();
        void monitor(
            const std::chrono::high_resolution_clock::duration& timeout,
            const std::atomic_bool& status
        );
    private:
        std::atomic_uint& get_count();

        std::atomic_uint count;
    };
}

#endif  // REVOLUTION_HEART_H
