#include "heart.h"

#include <atomic>
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <thread>

namespace Revolution {
    const std::atomic_uint& Heart::get_count() const {
        return count;
    }

    void Heart::beat() {
        ++get_count();
    }

    void Heart::monitor(
            const std::chrono::high_resolution_clock::duration& timeout,
            const std::atomic_bool& status
    ) {
        get_count() = 1;

        while (status) {
            if (!get_count()) {
                std::cerr << "No heartbeat within the timeout! "
                    << "Heart attack occurred. Aborting..."
                    << std::endl;

                std::abort();
            }

            get_count() = 0;

            std::this_thread::sleep_for(timeout);
        }
    }

    std::atomic_uint& Heart::get_count() {
        return count;
    }
}
