#include "peripheral.h"

#include <functional>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>

#include "application.h"
#include "configuration.h"
#include "message.h"
#include "logger.h"

namespace Revolution {
    Peripheral::Peripheral(
            const std::reference_wrapper<const Header_space>& header_space,
            const std::reference_wrapper<const State_space>& state_space,
            const std::reference_wrapper<const Topology>& topology,
            const unsigned int& thread_count
    ) :
        Application{header_space, state_space, topology, thread_count},
        watchers{},
        mutex{} {}

    std::optional<std::string> Peripheral::get_state(const std::string& key) {
        auto message = communicate(
            get_topology().get_database_name(),
            get_header_space().get_state_header(),
            {key}
        );

        if (message.get_data().size() != 1) {
            if (!message.get_data().empty())
                get_logger() << Logger::Severity::error
                    << "Unexpected elements in the reply."
                    << std::endl;

            return std::nullopt;
        }

        return message.get_data().front();
    }

    void Peripheral::set_state(
            const std::string& key,
            const std::string& value
    ) {
        communicate(
            get_topology().get_database_name(),
            get_header_space().get_state_header(),
            {key, value}
        );
    }

    void Peripheral::set_watcher(
            const std::string& key,
            const std::function<void(const std::string&, const std::string&)>&
                watcher
    ) {
        std::scoped_lock lock{get_mutex()};

        get_watchers()[key] = watcher;
    }

    void Peripheral::setup() {
        Application::setup();

        set_handler(
            get_header_space().get_state_header(),
            std::bind(&Peripheral::handle_state, this, std::placeholders::_1)
        );
    }

    const std::unordered_map<
            std::string,
            std::function<void(const std::string&, const std::string&)>
    >& Peripheral::get_watchers() const {
        return watchers;
    }

    const std::mutex& Peripheral::get_mutex() const {
        return mutex;
    }

    std::unordered_map<
            std::string,
            std::function<void(const std::string&, const std::string&)>
    >& Peripheral::get_watchers() {
        return watchers;
    }

    std::mutex& Peripheral::get_mutex() {
        return mutex;
    }

    std::optional<
            const std::reference_wrapper<
                const std::function<
                    void(const std::string&, const std::string&)
                >
            >
    > Peripheral::get_watcher(const std::string& key) {
        std::scoped_lock lock{get_mutex()};

        if (!get_watchers().count(key))
            return std::nullopt;

        return get_watchers().at(key);
    }

    std::vector<std::string> Peripheral::handle_state(const Message& message) {
        if (message.get_data().size() != 2) {
            get_logger() << Logger::Severity::error
                << "State expects 2 arguments, but "
                << message.get_data().size()
                << " argument(s) were supplied. "
                << "The message will be ignored."
                << std::endl;

            return {};
        }

        const auto& key = message.get_data().front();
        const auto& value = message.get_data().back();
        const auto watcher = get_watcher(key);

        get_logger() << Logger::Severity::information
            << "The (key, value): (\""
            << key
            << "\", \""
            << value
            << "\") has been updated. "
            << "If a relevant watcher exists, it will be invoked..."
            << std::endl;

        if (watcher)
            watcher.value()(key, value);

        return {};
    }
}
