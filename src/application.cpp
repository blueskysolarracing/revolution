#include "application.h"

namespace Revolution {
Application::Application(const std::string &name)
    : name_{name}, messageQueue_{name} {
  getLogger(LogLevel::INFO) << "Starting " << getName() << "..." << std::endl;
}

Application::~Application() {
  getLogger(LogLevel::INFO) << "Exiting " << getName() << "..." << std::endl;
}

Logger &Application::getLogger(LogLevel logLevel) const {
  return std::cout;  // TODO: CHECK LOG LEVEL
}

const std::string &Application::getName() const {
  return name_;
}

MessageQueue &Application::getMessageQueue() {
  return messageQueue_;
}
}
