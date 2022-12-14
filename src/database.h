#ifndef REVOLUTION_DATABASE_H
#define REVOLUTION_DATABASE_H

#include <atomic>
#include <chrono>
#include <functional>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

#include "application.h"
#include "configuration.h"
#include "message.h"

namespace Revolution {
    class Database : public Application {
    public:
        explicit Database(
            const std::reference_wrapper<const Header_space>& header_space,
            const std::reference_wrapper<const State_space>& state_space,
            const std::reference_wrapper<const Topology>& topology,
            const unsigned int& thread_count = get_default_thread_count()
        );
    protected:
        void setup() override;
    private:
        static const unsigned int default_thread_count;
        static const std::chrono::high_resolution_clock::duration timeout;

        static const unsigned int& get_default_thread_count();
        static const std::chrono::high_resolution_clock::duration&
            get_timeout();

        const std::string& get_name() const override;
        const std::chrono::high_resolution_clock::duration&
            get_message_queue_timeout() const override;

        const std::unordered_map<std::string, std::string>& get_states() const;
        const std::mutex& get_mutex() const;

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
