#include "application.h"

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdlib>
#include <functional>
#include <mutex>
#include <optional>
#include <ostream>
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
    Application::Application(
            const std::reference_wrapper<const Header_space>& header_space,
            const std::reference_wrapper<const State_space>& state_space,
            const std::reference_wrapper<const Topology>& topology,
            const unsigned int& thread_count
    ) :
            header_space{header_space},
            state_space{state_space},
            topology{topology},
            thread_pool{thread_count} {}

    void Application::main() {
        get_logger() << Logger::Severity::information
            << "Starting: \""
            << get_name()
            << "\"..."
            << std::endl;

        setup();
        run();

        get_logger() << Logger::Severity::information
            << "Stopping: \""
            << get_name()
            << "\"..."
            << std::endl;
    }

    const Header_space& Application::get_header_space() const {
        return header_space;
    }

    const State_space& Application::get_state_space() const {
        return state_space;
    }

    const Topology& Application::get_topology() const {
        return topology;
    }

    const Logger& Application::get_logger() const {
        return logger;
    }

    const Heart& Application::get_heart() const {
        return heart;
    }

    const Thread_pool& Application::get_thread_pool() const {
        return thread_pool;
    }

    const std::atomic_bool& Application::get_status() const {
        return status;
    }

    Heart& Application::get_heart() {
        return heart;
    }

    Thread_pool& Application::get_thread_pool() {
        return thread_pool;
    }

    std::atomic_bool& Application::get_status() {
        return status;
    }

    void Application::set_handler(
            const std::string& header,
            const std::function<std::vector<std::string>(const Message&)>&
                handler
    ) {
        std::scoped_lock lock{get_handler_mutex()};

        if (get_handlers().count(header))
            get_logger() << Logger::Severity::warning
                << "Overriding an existing handler: \""
                << header
                << "\"..."
                << std::endl;
        else
            get_logger() << Logger::Severity::information
                << "Adding handler: \""
                << header
                << "\"..."
                << std::endl;

        get_handlers()[header] = handler;
    }

    Message Application::send(
            const std::string& receiver_name,
            const std::string& header,
            const std::vector<std::string>& data,
            const unsigned int& priority,
            const std::optional<unsigned int>& identifier
    ) {
        Message message{
            get_name(),
            receiver_name,
            header,
            data,
            priority,
            identifier
        };
        MessageQueue message_queue{'/' + receiver_name};

        message_queue.send(message.serialize(), priority);

        return message;
    }

    Message Application::communicate(
            const std::string& receiver_name,
            const std::string& header,
            const std::vector<std::string>& data,
            const unsigned int& priority,
            const std::optional<unsigned int>& identifier
    ) {
        auto message = send(
            receiver_name,
            header,
            data,
            priority,
            identifier
        );

        return get_response(message);
    }

    void Application::setup() {
        get_status() = true;

        get_logger() << Logger::Severity::information
            << "Adding handlers..."
            << std::endl;

        set_handler(
            get_header_space().get_abort_header(),
            std::bind(&Application::handle_abort, this, std::placeholders::_1)
        );
        set_handler(
            get_header_space().get_exit_header(),
            std::bind(&Application::handle_exit, this, std::placeholders::_1)
        );
        set_handler(
            get_header_space().get_response_header(),
            std::bind(
                &Application::handle_response,
                this,
                std::placeholders::_1
            )
        );
        set_handler(
            get_header_space().get_status_header(),
            std::bind(&Application::handle_status, this, std::placeholders::_1)
        );
    }

    const std::unordered_map<
            std::string,
            std::function<std::vector<std::string>(const Message&)>
    >& Application::get_handlers() const {
        return handlers;
    }

    const std::mutex& Application::get_handler_mutex() const {
        return handler_mutex;
    }

    const std::unordered_map<unsigned int, std::optional<Message>>&
            Application::get_responses() const {
        return responses;
    }

    const std::mutex& Application::get_response_mutex() const {
        return response_mutex;
    }

    const std::condition_variable&
            Application::get_response_condition_variable() const {
        return response_condition_variable;
    }

    std::unordered_map<
            std::string,
            std::function<std::vector<std::string>(const Message&)>
    >& Application::get_handlers() {
        return handlers;
    }

    std::mutex& Application::get_handler_mutex() {
        return handler_mutex;
    }

    std::unordered_map<unsigned int, std::optional<Message>>&
            Application::get_responses() {
        return responses;
    }

    std::mutex& Application::get_response_mutex() {
        return response_mutex;
    }

    std::condition_variable& Application::get_response_condition_variable() {
        return response_condition_variable;
    }

    std::optional<
            const std::reference_wrapper<
                const std::function<std::vector<std::string>(const Message&)>
            >
    > Application::get_handler(const std::string& header) {
        std::scoped_lock lock{get_handler_mutex()};

        if (!get_handlers().count(header))
            return std::nullopt;

        return get_handlers().at(header);
    }

    Message Application::get_response(const Message& message) {
        std::unique_lock lock{get_response_mutex()};

        get_responses().emplace(message.get_identifier(), std::nullopt);

        while (!get_responses().at(message.get_identifier()))
            get_response_condition_variable().wait(lock);

        auto response = get_responses().at(message.get_identifier()).value();

        get_responses().erase(message.get_identifier());

        return response;
    }

    void Application::set_response(const Message& message) {
        std::unique_lock lock{get_response_mutex()};

        if (get_responses().count(message.get_identifier())) {
            get_responses().erase(message.get_identifier());
            get_responses().emplace(message.get_identifier(), message);
            get_response_condition_variable().notify_all();
        }
    }

    std::vector<std::string>
            Application::handle_abort(const Message& message) const {
        if (!message.get_data().empty()) {
            get_logger() << Logger::Severity::error
                << "Abort expects no arguments, but "
                << message.get_data().size()
                << " argument(s) were supplied. "
                << "This message will be ignored."
                << std::endl;
            
            return {};
        }

        get_logger() << Logger::Severity::information
            << "Aborting..."
            << std::endl;

        std::abort();
    }

    std::vector<std::string> Application::handle_exit(const Message& message) {
        if (!message.get_data().empty()) {
            get_logger() << Logger::Severity::error
                << "Exit expects no arguments, but "
                << message.get_data().size()
                << " argument(s) were supplied. "
                << "This message will be ignored."
                << std::endl;

            return {};
        }

        get_logger() << Logger::Severity::information
            << "Exiting gracefully..."
            << std::endl;

        get_status() = false;

        return {};
    }

    std::vector<std::string>
            Application::handle_response(const Message& message) {
        get_logger() << Logger::Severity::information
            << "Waking up a corresponding thread (if any)..."
            << std::endl;

        set_response(message);

        return {};
    }

    std::vector<std::string>
            Application::handle_status(const Message& message) const {
        if (!message.get_data().empty())
            get_logger() << Logger::Severity::warning
                << "Status expects no arguments, but "
                << message.get_data().size()
                << " argument(s) were supplied. "
                << "The argument(s) will be ignored."
                << std::endl;

        get_logger() << Logger::Severity::information
            << "Status report requested. Sending response..."
            << std::endl;

        return {};
    }

    void Application::handle(const Message& message) {
        if (message.get_header()
                == get_header_space().get_response_header()) {
            handle_response(message);

            return;
        }

        get_thread_pool().add(
            std::bind(&Application::help_handle, this, message)
        );
    }

    void Application::help_handle(const Message& message) {
        auto handler = get_handler(message.get_header());

        if (!handler) {
            get_logger() << Logger::Severity::warning
                << "Handler for message : "
                << message.to_string()
                << " is unknown. Skipping handling..."
                << std::endl;

            return;
        }

        auto data = handler.value()(message);

        get_logger() << Logger::Severity::information
            << "Sending response..."
            << std::endl;

        send(
            message.get_sender_name(),
            get_header_space().get_response_header(),
            data,
            message.get_priority(),
            message.get_identifier()
        );
    }

    void Application::run() {
        // TODO: check for hanging.
        // get_thread_pool().add(
        //     std::bind(
        //         &Heart::monitor,
        //         &get_heart(),
        //         get_timeout(),
        //         std::cref(get_status())
        //     )
        // );
        MessageQueue message_queue{'/' + get_name()};

        message_queue.monitor(
            get_status(),
            [this] (const std::string& raw_message) {
                auto message = Message::deserialize(raw_message);

                handle(message);
            },
            get_message_queue_timeout()
        );
    }
}
