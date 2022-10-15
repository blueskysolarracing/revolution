#include <iostream>
#include <thread>

#include "client.h"

void revolution::Client::run() {
	std::thread thread(&revolution::Client::helpRun, this);
	std::string message;

	while (message != "exit") {
		getline(std::cin, message);

		send(message, "echo");  // TODO: DO NOT HARD-CODE
	}

	exit_.store(true);
	thread.join();
}

unsigned int revolution::Client::getPriority() {
	return priority_;
}

revolution::Client::Client() : App{"client"} {}  // TODO: DO NOT HARD-CODE

void revolution::Client::helpRun() {
	while (!exit_.load()) {
		boost::posix_time::ptime absTime = boost::posix_time::microsec_clock::local_time() + pollingPeriod;
		std::string message = timedReceive(absTime);

		if (!message.empty())
			std::cout << message << std::endl;
	}
}

int main() {
	revolution::Client &client = revolution::Client::getInstance();

	client.run();

	return 0;
}
