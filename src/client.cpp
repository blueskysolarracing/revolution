#include <atomic>
#include <functional>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include "messenger.h"

void receiver(
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

void sender(
	const std::string& sender_name,
	const std::string& recipient_name,
	const Revolution::Messenger& messenger,
	std::atomic_bool& status
) {
	std::string header;
	std::vector<std::string> data;

	while (status.load()) {
		std::string input;
		std::getline(std::cin, input);

		if (input.empty())
			status = false;
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
}


int main(int argc, char *argv[]) {
	if (argc < 2) {
		std::cout << "Usage: "
			<< "./client "
			<< "sender_name "
			<< "[recipient_name header data...]"
			<< std::endl;

		return -1;
	}
	
	std::string sender_name{argv[1]};
	Revolution::Messenger messenger;
	std::atomic_bool status;

	if (argc == 2) {
		receiver(sender_name, messenger, status);

		return 0;
	} else if (argc == 3)
		status = true;

	std::string recipient_name{argv[2]};

	if (argc > 3) {
		std::string header{argv[3]};
		std::vector<std::string> data{std::next(argv, 4), std::next(argv, argc)};

		messenger.send(
			Revolution::Messenger::Message{
				sender_name,
				recipient_name,
				header,
				data
			}
		);
	}

	std::thread receiver_thread{
		receiver,
		sender_name,
		messenger,
		std::cref(status)
	};
	std::thread sender_thread{
		sender,
		sender_name,
		recipient_name,
		messenger,
		std::ref(status)
	};

	receiver_thread.join();
	sender_thread.join();

	return 0;
}
