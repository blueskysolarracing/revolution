#ifndef REVOLUTION_DATABASE_H
#define REVOLUTION_DATABASE_H

#include "application.h"

namespace Revolution {
    class Database : public Application {
    public:
        explicit Database(
            const HeaderSpace& header_space,
            const StateSpace& state_space,
            const Topology& topology,
            const unsigned int& thread_count = get_default_thread_count()
        );
    protected:
        void setup() override;
    private:
        static const unsigned int& get_default_thread_count();
        static const std::chrono::high_resolution_clock::duration&
            get_timeout();

        static const unsigned int default_thread_count;
        static const std::chrono::high_resolution_clock::duration timeout;

        const std::string& get_name() const override;
        const std::chrono::high_resolution_clock::duration&
            get_message_queue_timeout() const override;
        std::unordered_map<std::string, std::string>& get_states();
        std::mutex& get_mutex();
        std::vector<std::string> get_data();
        void set_data(const std::vector<std::string>& data);

        std::vector<std::string> handle_state(const Message& message);

        void sync();

        std::unordered_map<std::string, std::string> states;
        std::mutex mutex;
    };
}

#endif  // REVOLUTION_DATABASE_H
