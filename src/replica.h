#ifndef REVOLUTION_REPLICA_H
#define REVOLUTION_REPLICA_H

#include <chrono>
#include <functional>
#include <mutex>
#include <string>
#include <vector>

#include "application.h"
#include "configuration.h"
#include "message.h"

namespace Revolution {
    class Replica : public Application {
    public:
        explicit Replica(
            const std::reference_wrapper<const Header_space>& header_space,
            const std::reference_wrapper<const State_space>& state_space,
            const std::reference_wrapper<const Topology>& topology,
            const unsigned int& thread_count = get_default_thread_count()
        );
    protected:
        void setup() override;
    private:
        static const unsigned int default_thread_count;
        static const std::chrono::high_resolution_clock::duration
            message_queue_timeout;

        static const unsigned int& get_default_thread_count();

        const std::string& get_name() const override;
        const std::chrono::high_resolution_clock::duration&
            get_message_queue_timeout() const override;

        const std::vector<std::string>& get_data() const;
        const std::mutex& get_mutex() const;

        std::vector<std::string>& get_data();
        std::mutex& get_mutex();

        std::vector<std::string> handle_data(const Message& message);

        std::vector<std::string> data;
        std::mutex mutex;
    };
}

#endif  // REVOLUTION_REPLICA_H
