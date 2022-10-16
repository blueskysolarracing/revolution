#include "echo.h"

void revolution::Echo::run() {
	std::string message;

	while (message != "exit") {
		boost::posix_time::ptime absTime = boost::posix_time::microsec_clock::local_time() + pollingPeriod;
		message = timedReceive(absTime);

		if (!message.empty()) {
			std::cout << "Echoing message: " << message << std::endl;
			send(message, "client");  // TODO: DO NOT HARD-CODE
		}
	}
}

unsigned int revolution::Echo::getPriority() const {
	return priority_;
}

revolution::Echo::Echo() : App{"echo"} {}  // TODO: DO NOT HARD-CODE

int main() {
	revolution::Echo &echo = revolution::Echo::getInstance();

	echo.run();

	return 0;
}
