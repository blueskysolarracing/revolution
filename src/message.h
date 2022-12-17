#ifndef REVOLUTION_MESSAGE_H
#define REVOLUTION_MESSAGE_H

#include <optional>
#include <string>
#include <vector>

namespace Revolution {
    class Message {
    public:
        static Message deserialize(const std::string& raw_message);

        explicit Message(
            const std::string& sender_name,
            const std::string& receiver_name,
            const std::string& header,
            const std::vector<std::string>& data = {},
            const unsigned int& priority = 0,
            const std::optional<unsigned int>& identifier = std::nullopt
        );

        bool operator==(const Message& that) const;

        const std::string& get_sender_name() const;
        const std::string& get_receiver_name() const;
        const std::string& get_header() const;
        const std::vector<std::string>& get_data() const;
        const unsigned int& get_priority() const;
        const unsigned int& get_identifier() const;

        std::string serialize() const;
        std::string to_string() const;
    private:
        static unsigned int& get_count();

        static unsigned int count;

        const std::string sender_name;
        const std::string receiver_name;
        const std::string header;
        const std::vector<std::string> data;
        const unsigned int priority;
        const unsigned int identifier;
    };
}

#endif  // REVOLUTION_MESSAGE_H
