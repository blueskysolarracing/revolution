#include "power_sensor.h"

void revolution::PowerSensor::run() {  // TODO: ADD PROGRAM LOGIC
}

unsigned int revolution::PowerSensor::getPriority() {
	return priority_;
}

revolution::PowerSensor::PowerSensor() : Slave{"powerSensor"} {} // TODO: DO NOT HARD-CODE

int main() {
	revolution::PowerSensor &powerSensor = revolution::PowerSensor::getInstance();

	powerSensor.run();

	return 0;
}
