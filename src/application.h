#ifndef REVOLUTION_APPLICATION_H
#define REVOLUTION_APPLICATION_H

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <functional>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

#include "configuration.h"
#include "device.h"
#include "heart.h"
#include "logger.h"
#include "message.h"
#include "thread_pool.h"

namespace Revolution {
    class Application {
    public:
        explicit Application(
            const std::reference_wrapper<const Header_space>& header_space,
            const std::reference_wrapper<const State_space>& state_space,
            const std::reference_wrapper<const Topology>& topology,
            const unsigned int& thread_count
        );
        virtual ~Application() = default;

        void main();
    protected:
        const Header_space& get_header_space() const;
        const State_space& get_state_space() const;
        const Topology& get_topology() const;
        const Logger& get_logger() const;
        const Heart& get_heart() const;
        const Thread_pool& get_thread_pool() const;
        const std::atomic_bool& get_status() const;
        virtual const std::string& get_name() const = 0;
        virtual const std::chrono::high_resolution_clock::duration&
            get_message_queue_timeout() const = 0;

        Heart& get_heart();
        Thread_pool& get_thread_pool();
        std::atomic_bool& get_status();

        void set_handler(
            const std::string& header,
            const std::function<
                std::vector<std::string>(const Message&)
            >& handler
        );

        Message send(
            const std::string& receiver_name,
            const std::string& header,
            const std::vector<std::string>& data = {},
            const unsigned int& priority = 0,
            const std::optional<unsigned int>& identifier = std::nullopt
        );
        Message communicate(
            const std::string& receiver_name,
            const std::string& header,
            const std::vector<std::string>& data = {},
            const unsigned int& priority = 0,
            const std::optional<unsigned int>& identifier = std::nullopt
        );

        virtual void setup();
    private:
        const std::unordered_map<
            std::string,
            std::function<std::vector<std::string>(const Message&)>
        >& get_handlers() const;
        const std::mutex& get_handler_mutex() const;
        const std::unordered_map<unsigned int, std::optional<Message>>&
            get_responses() const;
        const std::mutex& get_response_mutex() const;
        const std::condition_variable&
            get_response_condition_variable() const;

        std::unordered_map<
            std::string,
            std::function<std::vector<std::string>(const Message&)>
        >& get_handlers();
        std::mutex& get_handler_mutex();
        std::unordered_map<unsigned int, std::optional<Message>>&
            get_responses();
        std::mutex& get_response_mutex();
        std::condition_variable& get_response_condition_variable();

        std::optional<
            const std::reference_wrapper<
                const std::function<std::vector<std::string>(const Message&)>
            >
        > get_handler(const std::string& header);
        Message get_response(const Message& message);
        void set_response(const Message& message);

        std::vector<std::string> handle_abort(const Message& message) const;
        std::vector<std::string> handle_exit(const Message& message);
        std::vector<std::string> handle_response(const Message& message);
        std::vector<std::string> handle_status(const Message& message) const;

        void handle(const Message& message);
        void help_handle(const Message& message);

        void run();

        const std::reference_wrapper<const Header_space> header_space;
        const std::reference_wrapper<const State_space> state_space;
        const std::reference_wrapper<const Topology> topology;
        const Logger logger;
        Heart heart;
        Thread_pool thread_pool;
        std::atomic_bool status;
        std::unordered_map<
            std::string,
            std::function<std::vector<std::string>(const Message&)>
        > handlers;
        std::mutex handler_mutex;
        std::unordered_map<
            unsigned int,
            std::optional<Message>
        > responses;
        std::mutex response_mutex;
        std::condition_variable response_condition_variable;
    };
}

#endif  // REVOLUTION_APPLICATION_H
