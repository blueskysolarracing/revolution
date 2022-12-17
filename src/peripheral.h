#ifndef REVOLUTION_PERIPHERAL_H
#define REVOLUTION_PERIPHERAL_H

#include "application.h"

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
