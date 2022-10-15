#include "motor_controller.h"

void revolution::MotorController::run() {  // TODO: ADD PROGRAM LOGIC
}

unsigned int revolution::MotorController::getPriority() {
	return priority_;
}

revolution::MotorController::MotorController() : Slave{"motorController"} {} // TODO: DO NOT HARD-CODE

int main() {
	revolution::MotorController &motorController = revolution::MotorController::getInstance();

	motorController.run();

	return 0;
}
