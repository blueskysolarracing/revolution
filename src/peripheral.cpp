#include "peripheral.h"

#include <ostream>

namespace Revolution {
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

        if (get_watchers().count(key))
            get_logger() << Logger::Severity::warning
                << "Overriding an existing watcher: \""
                << key
                << "\"..."
                << std::endl;
        else
            get_logger() << Logger::Severity::information
                << "Adding watcher: \""
                << key
                << "\"..."
                << std::endl;

        get_watchers()[key] = watcher;
    }

    void Peripheral::setup() {
        Application::setup();

        set_handler(
            get_header_space().get_state_header(),
            std::bind(&Peripheral::handle_state, this, std::placeholders::_1)
        );
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
                << " argument(s) were supplied. The message will be ignored."
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
            << "\") has been updated. Any relevant watchers will be invoked..."
            << std::endl;

        if (watcher)
            (*watcher)(key, value);

        return {};
    }
}
