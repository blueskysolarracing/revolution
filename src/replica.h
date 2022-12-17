#ifndef REVOLUTION_REPLICA_H
#define REVOLUTION_REPLICA_H

#include "application.h"

namespace Revolution {
    class Replica : public Application {
    public:
        explicit Replica(
            const HeaderSpace& header_space,
            const StateSpace& state_space,
            const Topology& topology,
            const unsigned int& thread_count = get_default_thread_count()
        );
    protected:
        void setup() override;
    private:
        static const unsigned int& get_default_thread_count();

        static const unsigned int default_thread_count;
        static const std::chrono::high_resolution_clock::duration
            message_queue_timeout;

        const std::string& get_name() const override;
        const std::chrono::high_resolution_clock::duration&
            get_message_queue_timeout() const override;

        std::vector<std::string>& get_data();
        std::mutex& get_mutex();

        std::vector<std::string> handle_data(const Message& message);

        std::vector<std::string> data;
        std::mutex mutex;
    };
}

#endif  // REVOLUTION_REPLICA_H
