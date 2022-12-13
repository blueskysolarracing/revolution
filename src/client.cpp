#include <atomic>
#include <chrono>
#include <functional>
#include <iostream>
#include <iterator>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include "messenger.h"

const std::chrono::high_resolution_clock::duration timeout{
	std::chrono::microseconds{100}
};

int main(int argc, char *argv[]) {
	if (argc < 2) {
		std::cout << "Usage: "
			<< "./client sender_name [receiver_name header data...]"
			<< std::endl;

		return -1;
	}

	std::string sender_name{argv[1]};
	Revolution::Messenger messenger{sender_name};
	std::atomic_bool status{true};
	std::thread thread{
		&Revolution::Messenger::monitor,
		&messenger,
		timeout,
		std::cref(status),
		[] (const Revolution::Messenger::Message& message) {
			std::cout << message.to_string() << std::endl;
		}
	};

	if (argc == 2)
		std::cin.get();
	else {
		std::string receiver_name{argv[2]};

		if (argc > 3) {
			std::string header{argv[3]};
			std::vector<std::string> data{
				std::next(argv, 4),
				std::next(argv, argc)
			};

			messenger.send(receiver_name, header, data);
		}

		std::string header;
		std::vector<std::string> data;

		while (status) {
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

				messenger.send(receiver_name, header, data);

				header.clear();
				data.clear();
			}
		}
	}

	status = false;
	thread.join();

	return 0;
}
