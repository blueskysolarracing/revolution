#include "echo.h"

void revolution::Echo::run() {
  bool status = true;

  while (status) {
    boost::posix_time::ptime absTime = boost::posix_time::microsec_clock::local_time() + pollingPeriod;
    Message message = timedReceive(absTime);

    if (!message.getContent().empty()) {
      std::cout << "Echoing message from " << message.getSenderName() << ": " << message.getContent() << std::endl;
      send(message.getContent(), "client");  // TODO: DO NOT HARD-CODE
    }

    status = message.getContent() != "exit";
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
