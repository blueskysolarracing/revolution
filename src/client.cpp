#include <thread>

#include "client.h"

namespace revolution {
Client::Client(const std::string &name, const std::string &recipientName)
	: Application{name}, recipientName_{recipientName} {
}

const std::string &Client::getRecipientName() const {
	return recipientName_;
}

void Client::run() {
  std::thread thread(&Client::helpRun, this);
  std::string typeName;

  for (;;) {
    getline(std::cin, typeName);

    getMessageQueue().send(getRecipientName(), typeName);
  }
}

void Client::helpRun() {
  for(;;) {
    Message message = getMessageQueue().receive();

    getLogger(LogLevel::INFO) << message.getTypeName() << std::endl;
  }
}
}

int main(int argc, char *argv[]) {
  if (argc != 3) {std::cout << "invalid arg count" << std::endl; return 0; }
  std::string name(argv[1]), recipientName(argv[2]);
  revolution::Client client{name, recipientName};

  client.run();

  return 0;
}
