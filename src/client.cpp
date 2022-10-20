#include <thread>
#include <sstream>

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
  std::string line;

  while (std::getline(std::cin, line)) {
    if (line.empty())
	    continue;

    std::istringstream iss(line);
    std::string typeName;
    std::string argument;
    std::vector<std::string> arguments;

    iss >> typeName;

    while (std::getline(iss, argument, ' '))
      if (!argument.empty())
        arguments.push_back(argument);

    getMessageQueue().send(getRecipientName(), typeName, arguments);
  }
}

void Client::helpRun() {
  for(;;) {
    auto message = getMessageQueue().receive();
    auto &logger = getLogger(LogLevel::INFO);

    logger << message.getSenderName()
	    << ": " << message.getTypeName() << '(';

    auto arguments = message.getArguments();
    
    for (auto &argument : arguments)
	    logger << argument << ", ";

    logger << ')' << std::endl;
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
