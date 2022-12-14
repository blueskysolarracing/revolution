#ifndef REVOLUTION_PERIPHERAL_H
#define REVOLUTION_PERIPHERAL_H

#include <functional>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>

#include "application.h"
#include "configuration.h"
#include "message.h"

namespace Revolution {
    class Peripheral : public Application {
    public:
        using Application::Application;
    protected:
        std::optional<std::string> get_state(const std::string& key);
        void set_state(const std::string& key, const std::string& value);
        void set_watcher(
            const std::string& key,
            const std::function<void(const std::string&, const std::string&)>&
                watcher
        );

        virtual void setup() override;
    private:
        const std::unordered_map<
            std::string,
            std::function<void(const std::string&, const std::string&)>
        >& get_watchers() const;
        const std::mutex& get_mutex() const;

        std::unordered_map<
            std::string,
            std::function<void(const std::string&, const std::string&)>
        >& get_watchers();
        std::mutex& get_mutex();

        std::optional<
            const std::reference_wrapper<
                const std::function<
                    void(const std::string&, const std::string&)
                >
            >
        > get_watcher(const std::string& key);

        std::vector<std::string> handle_state(const Message& message);

        std::unordered_map<
            std::string,
            std::function<void(const std::string&, const std::string&)>
        > watchers;
        std::mutex mutex;
    };
}

#endif  // REVOLUTION_PERIPHERAL_H
