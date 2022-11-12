#include <atomic>
#include <chrono>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include "messenger.h"

void monitor(
	const std::string& recipient_name,
	const Revolution::Messenger& messenger,
	const std::atomic_bool& status
) {
	auto received = true;

	while (status || received) {
		auto optional_message = messenger.timed_receive(recipient_name);
		received = optional_message.has_value();

		if (received)
			std::cout << optional_message.value().serialize()
				<< std::endl;
	}
}

int main(int argc, char *argv[]) {
	if (argc < 3) {
		std::cout << "Usage: "
			<< "./client "
			<< "sender_name "
			<< "recipient_name "
			<< "[header data...]"
			<< std::endl;

		return 0;
	}

	std::string sender_name{argv[1]};
	std::string recipient_name{argv[2]};
	std::string header;
	std::vector<std::string> data;
	Revolution::Messenger messenger;
	std::atomic_bool status{true};

	if (argc > 3) {
		header = argv[3];

		for (int i{4}; i < argc; ++i)
			data.emplace_back(argv[i]);

		messenger.send(
			Revolution::Messenger::Message{
				sender_name,
				recipient_name,
				header,
				data
			}
		);
		status.store(false);
	}

	std::thread thread{monitor, sender_name, messenger, std::cref(status)};

	while (status.load()) {
		std::string input;
		std::getline(std::cin, input);

		if (input.empty())
			status.store(false);
		else {
			std::istringstream iss(input);
			std::string datum;

			iss >> header;

			while (iss >> datum)
				data.push_back(datum);

			messenger.send(
				Revolution::Messenger::Message{
					sender_name,
					recipient_name,
					header,
					data
				}
			);

			header.clear();
			data.clear();
		}
	}

	thread.join();

	return 0;
}
