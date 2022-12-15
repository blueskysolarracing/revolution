#include "replica.h"

#include <chrono>
#include <functional>
#include <mutex>
#include <ostream>
#include <string>
#include <vector>

#include "application.h"
#include "configuration.h"
#include "logger.h"
#include "message.h"

namespace Revolution {
    Replica::Replica(
            const HeaderSpace& header_space,
            const StateSpace& state_space,
            const Topology& topology,
            const unsigned int& thread_count
    ) : Application{header_space, state_space, topology, thread_count} {}

    void Replica::setup() {
        Application::setup();

        set_handler(
            get_header_space().get_data_header(),
            std::bind(&Replica::handle_data, this, std::placeholders::_1)
        );
    }

    const unsigned int Replica::default_thread_count{4};

    const std::chrono::high_resolution_clock::duration
            Replica::message_queue_timeout{
        std::chrono::seconds(1)
    };

    const unsigned int& Replica::get_default_thread_count() {
        return default_thread_count;
    }

    const std::string& Replica::get_name() const {
        return get_topology().get_replica_name();
    }

    const std::chrono::high_resolution_clock::duration&
            Replica::get_message_queue_timeout() const {
        return message_queue_timeout;
    }

    const std::vector<std::string>& Replica::get_data() const {
        return data;
    }

    const std::mutex& Replica::get_mutex() const {
        return mutex;
    }

    std::vector<std::string>& Replica::get_data() {
        return data;
    }

    std::mutex& Replica::get_mutex() {
        return mutex;
    }

    std::vector<std::string> Replica::handle_data(const Message& message) {
        std::scoped_lock lock{get_mutex()};

        if (message.get_data().empty()) {
            get_logger() << Logger::Severity::information
                << "Retrieving data..."
                << std::endl;

            return get_data();
        } else if (message.get_data().size() % 2 == 0) {
            get_logger() << Logger::Severity::information
                << "Storing data..."
                << std::endl;

            get_data() = message.get_data();

            return {};
        }

        get_logger() << Logger::Severity::error
            << "Data expects 2 * n arguments (n >= 0), but "
            << message.get_data().size()
            << " argument(s) were supplied. "
            << "This message will be ignored."
            << std::endl;

        return {};
    }
}

int main() {
    Revolution::HeaderSpace header_space;
    Revolution::StateSpace state_space;
    Revolution::Topology topology;
    Revolution::Replica replica{header_space, state_space, topology};

    replica.main();

    return 0;
}
