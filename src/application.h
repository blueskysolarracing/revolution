#ifndef REVOLUTION_APPLICATION_H_
#define REVOLUTION_APPLICATION_H_

#include "message_queue.h"
#include "logger.h"

namespace revolution {
class Application {
public:
  explicit Application(const std::string &name);
  ~Application();

  virtual void run() = 0;
protected:
  Logger &getLogger(LogLevel logLevel) const;
  const std::string &getName() const;
  MessageQueue &getMessageQueue();
private:
  const std::string name_;
  MessageQueue messageQueue_;
};
}

#endif  // REVOLUTION_APPLICATION_H_
