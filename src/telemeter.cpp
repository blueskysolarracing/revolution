#include "telemeter.h"

void revolution::Telemeter::run() {  // TODO: ADD PROGRAM LOGIC
}

unsigned int revolution::Telemeter::getPriority() {
	return priority_;
}

revolution::Telemeter::Telemeter() : Slave{"telemeter"} {}  // TODO: DO NOT HARD-CODE

int main() {
	revolution::Telemeter &telemeter = revolution::Telemeter::getInstance();

	telemeter.run();

	return 0;
}
