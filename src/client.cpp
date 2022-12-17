#include <atomic>
#include <chrono>
#include <functional>
#include <iostream>
#include <iterator>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include "device.h"
#include "message.h"

const std::chrono::high_resolution_clock::duration timeout{
    std::chrono::microseconds{100}
};

int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cout << "Usage: "
            << "./client client_name [target_name header data...]"
            << std::endl;

        return -1;
    }

    std::string client_name{argv[1]};
    Revolution::MessageQueue client_message_queue{'/' + client_name};
    std::atomic_bool status{true};
    std::thread thread{
        [&client_message_queue, &status] () {
            client_message_queue.monitor(
                status,
                timeout,
                [] (const std::string& raw_message) {
                    auto message = Revolution::Message::deserialize(
                        raw_message
                    );

                    std::cout << message.to_string() << std::endl;
                }
            );
        }
    };

    if (argc == 2)
        std::cin.get();
    else {
        std::string target_name{argv[2]};
        Revolution::MessageQueue target_message_queue{'/' + target_name};

        if (argc > 3) {
            std::string header{argv[3]};
            std::vector<std::string> data{
                std::next(argv, 4),
                std::next(argv, argc)
            };
            Revolution::Message message{
                client_name,
                target_name,
                header,
                data
            };

            target_message_queue.send(
                message.serialize(),
                message.get_priority()
            );
        }

        while (status) {
            std::string input;
            std::string header;
            std::vector<std::string> data;

            std::getline(std::cin, input);

            if (input.empty())
                status = false;
            else {
                std::istringstream iss(input);
                std::string datum;

                iss >> header;

                while (iss >> datum)
                    data.push_back(datum);

                Revolution::Message message{
                    client_name,
                    target_name,
                    header,
                    data
                };

                target_message_queue.send(
                    message.serialize(),
                    message.get_priority()
                );
                header.clear();
                data.clear();
            }
        }
    }

    status = false;
    thread.join();
    client_message_queue.unlink();

    return 0;
}
