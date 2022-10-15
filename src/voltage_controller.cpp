#include "voltage_controller.h"

void revolution::VoltageController::run() {  // TODO: ADD PROGRAM LOGIC
}

unsigned int revolution::VoltageController::getPriority() {
	return priority_;
}

revolution::VoltageController::VoltageController() : Slave{"voltageController"} {}  // TODO: DO NOT HARD-CODE

int main() {
	revolution::VoltageController &voltageController = revolution::VoltageController::getInstance();

	voltageController.run();

	return 0;
}
