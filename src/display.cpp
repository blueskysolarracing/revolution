#include "display.h"

#include <chrono>
#include <string>

#include "configuration.h"
#include "peripheral.h"

namespace Revolution {
    Display::Display(
            const HeaderSpace& header_space,
            const StateSpace& state_space,
            const Topology& topology,
            const unsigned int& thread_count
    ) : Peripheral{header_space, state_space, topology, thread_count} {}

    const unsigned int Display::default_thread_count{4};

    const std::chrono::high_resolution_clock::duration
            Display::message_queue_timeout{
        std::chrono::seconds(1)
    };

    const unsigned int& Display::get_default_thread_count() {
        return default_thread_count;
    }

    const std::string& Display::get_name() const {
        return get_topology().get_display_name();
    }

    const std::chrono::high_resolution_clock::duration&
            Display::get_message_queue_timeout() const {
        return message_queue_timeout;
    }
}

int main() {
    Revolution::HeaderSpace header_space;
    Revolution::StateSpace state_space;
    Revolution::Topology topology;
    Revolution::Display display{header_space, state_space, topology};

    display.main();

    return 0;
}
