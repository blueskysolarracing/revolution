#ifndef REVOLUTION_DISPLAY_H
#define REVOLUTION_DISPLAY_H

#include <chrono>
#include <string>

#include "configuration.h"
#include "peripheral.h"

namespace Revolution {
    class Display : public Peripheral {
    public:
        explicit Display(
            const HeaderSpace& header_space,
            const StateSpace& state_space,
            const Topology& topology,
            const unsigned int& thread_count = get_default_thread_count()
        );
    private:
        static const unsigned int default_thread_count;
        static const std::chrono::high_resolution_clock::duration
            message_queue_timeout;

        static const unsigned int& get_default_thread_count();

        const std::string& get_name() const override;
        const std::chrono::high_resolution_clock::duration&
            get_message_queue_timeout() const override;
    };
}

#endif  // REVOLUTION_DISPLAY_H
