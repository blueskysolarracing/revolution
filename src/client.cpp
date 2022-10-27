#include <atomic>
#include <chrono>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include "logger.h"
#include "messenger.h"

void monitor(
	const Revolution::Messenger& messenger,
	const std::atomic_bool& status
)
{
	static constexpr std::chrono::high_resolution_clock::duration monitor_timeout
		= std::chrono::milliseconds(100);

	while (status.load()) {
		auto optional_message = messenger.receive(monitor_timeout);

		if (optional_message.has_value())
			std::cout << optional_message.value().to_string()
				<< std::endl;
	}
}

int main(int argc, char *argv[])
{
	if (argc < 3) {
		std::cout << "Usage: ./client "
			<< "sender_name recipient_name "
			<< "[header] [data...]" << std::endl;

		return 0;
	}

	std::string sender_name(argv[1]);
	std::string recipient_name(argv[2]);
	std::string header;
	std::vector<std::string> data;
	Revolution::Logger logger{
		Revolution::Logger::Configuration{Revolution::Logger::fatal}
	};
	Revolution::Messenger messenger{
		Revolution::Messenger::Configuration{sender_name},
		logger
	};
	std::atomic_bool status{true};

	if (argc > 3) {
		header = argv[3];

		for (int i = 4; i < argc; ++i)
			data.emplace_back(argv[i]);

		messenger.send(recipient_name, header, data);
		status.store(false);
	}

	std::thread thread{monitor, messenger, std::ref(status)};

	while (status.load()) {
		std::string input;
		std::getline(std::cin, input);
		std::istringstream iss(input);

		iss >> header;

		std::string datum;

		while (std::getline(iss, datum, ' '))
			if (!datum.empty())
				data.push_back(datum);

		if (header.empty())
			status.store(false);
		else
			messenger.send(recipient_name, header, data);

		header.clear();
		data.clear();
	}

	thread.join();

	return 0;
}
