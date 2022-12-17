#include "message.h"

#include <cstddef>
#include <iterator>
#include <sstream>

namespace Revolution {
    Message Message::deserialize(const std::string& raw_message) {
        std::vector<std::string> tokens;
        std::size_t begin_index{};
        auto end_index = raw_message.find('\0');

        while (end_index != std::string::npos) {
            tokens.push_back(
                raw_message.substr(begin_index, end_index - begin_index)
            );
            begin_index = end_index + 1;
            end_index = raw_message.find('\0', begin_index);
        }

        auto sender_name = tokens[0];
        auto receiver_name = tokens[1];
        auto header = tokens[2];
        std::vector<std::string> data{
            std::next(tokens.begin(), 3),
            std::next(tokens.begin(), tokens.size() - 2)
        };
        auto priority = (unsigned int) std::stoul(tokens[tokens.size() - 2]);
        auto identifier = (unsigned int) std::stoul(tokens[tokens.size() - 1]);

        return Message{
            sender_name,
            receiver_name,
            header,
            data,
            priority,
            identifier
        };
    }

    Message::Message(
            const std::string& sender_name,
            const std::string& receiver_name,
            const std::string& header,
            const std::vector<std::string>& data,
            const unsigned int& priority,
            const std::optional<unsigned int>& identifier
    ) :
            sender_name{sender_name},
            receiver_name{receiver_name},
            header{header},
            data{data},
            priority{priority},
            identifier{identifier ? *identifier : get_count()++} {}

    bool Message::operator==(const Message& that) const {
        return get_sender_name() == that.get_sender_name()
            && get_receiver_name() == that.get_receiver_name()
            && get_header() == that.get_header()
            && get_data() == that.get_data()
            && get_priority() == that.get_priority()
            && get_identifier() == that.get_identifier();
    }

    const std::string& Message::get_sender_name() const {
        return sender_name;
    }

    const std::string& Message::get_receiver_name() const {
        return receiver_name;
    }

    const std::string& Message::get_header() const {
        return header;
    }

    const std::vector<std::string>& Message::get_data() const {
        return data;
    }

    const unsigned int& Message::get_priority() const {
        return priority;
    }

    const unsigned int& Message::get_identifier() const {
        return identifier;
    }

    std::string Message::serialize() const {
        std::ostringstream oss;

        oss << get_sender_name()
            << '\0'
            << get_receiver_name()
            << '\0'
            << get_header()
            << '\0';

        for (const auto& datum : get_data())
            oss << datum << '\0';

        oss << get_priority() << '\0' << get_identifier() << '\0';

        return oss.str();
    }

    std::string Message::to_string() const {
        std::ostringstream oss;

        oss << "{\"sender_name\": \""
            << get_sender_name()
            << "\", \"receiver_name\": \""
            << get_receiver_name()
            << "\", \"header\": \""
            << get_header()
            << "\", \"data\": [";

        auto it = get_data().begin();

        if (it != get_data().end())
            oss << "\"" << *it++ << "\"";

        while (it != get_data().end())
            oss << ", \"" << *it++ << "\"";

        oss << "], \"priority\": "
            << get_priority()
            << ", \"identifier\": "
            << get_identifier()
            << "}";

        return oss.str();
    }

    unsigned int& Message::get_count() {
        return count;
    }

    unsigned int Message::count{};
}
