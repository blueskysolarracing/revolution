#include "echo.h"

void revolution::Echo::run() {
	std::string message;

	while (message != "exit") {
		message = receive();

		send(message, "client");  // TODO: DO NOT HARD-CODE
	}
}

unsigned int revolution::Echo::getPriority() {
	return priority_;
}

revolution::Echo::Echo() : App{"echo"} {} // TODO: DO NOT HARD-CODE

int main() {
	revolution::Echo &echo = revolution::Echo::getInstance();

	echo.run();

	return 0;
}
