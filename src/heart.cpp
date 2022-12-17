#include "heart.h"

#include <cstdlib>
#include <iostream>
#include <thread>

namespace Revolution {
    void Heart::beat() {
        ++get_count();
    }

    void Heart::monitor(
            const std::atomic_bool& status,
            const std::chrono::high_resolution_clock::duration& timeout,
            const std::function<void()>& callback
    ) {
        while (status) {
            get_count() = 0;
            callback();
            std::this_thread::sleep_for(timeout);

            if (!get_count()) {
                std::cerr << "No heartbeat within the timeout... Heart attack!"
                    << std::endl;

                std::abort();
            }
        }
    }

    std::atomic_uint& Heart::get_count() {
        return count;
    }
}
