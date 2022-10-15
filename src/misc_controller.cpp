#include "misc_controller.h"

void revolution::MiscController::run() {  // TODO: ADD PROGRAM LOGIC
}

unsigned int revolution::MiscController::getPriority() {
	return priority_;
}

revolution::MiscController::MiscController() : Slave{"miscController"} {}  // TODO: DO NOT HARD-CODE

int main() {
	revolution::MiscController &miscController = revolution::MiscController::getInstance();

	miscController.run();

	return 0;
}
