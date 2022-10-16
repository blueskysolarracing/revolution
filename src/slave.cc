#include "slave.h"

revolution::Slave::Slave(const std::string &name) : App{name} {}

revolution::Slave::~Slave() {}

void revolution::Slave::sendMaster(const std::string &message) const {
  send(message, "syncer");  // TODO: DO NOT HARD-CODE
}
