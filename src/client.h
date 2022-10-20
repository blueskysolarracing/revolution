#ifndef REVOLUTION_CLIENT_H
#define REVOLUTION_CLIENT_H

#include "application.h"

namespace Revolution {
class Client : public Application {
public:
  explicit Client(const std::string &name, const std::string &recipientName);

  const std::string &getRecipientName() const;

  void run() override;
private:
  void helpRun();

  std::string recipientName_;
};
}

#endif  // REVOLUTION_CLIENT_H
