#include "slave.h"

revolution::Slave::Slave(std::string name) : App{name} {}

revolution::Slave::~Slave() {}

void revolution::Slave::sendMaster(std::string message) {
	send(message, "syncer");  // TODO: DO NOT HARD-CODE
}
