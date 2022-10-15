#include "display_driver.h"

void revolution::DisplayDriver::run() {  // TODO: ADD PROGRAM LOGIC
}

unsigned int revolution::DisplayDriver::getPriority() {
	return priority_;
}

revolution::DisplayDriver::DisplayDriver() : Slave{"displayDriver"} {}  // TODO: DO NOT HARD-CODE

int main() {
	revolution::DisplayDriver &displayDriver = revolution::DisplayDriver::getInstance();

	displayDriver.run();

	return 0;
}
