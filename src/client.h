#ifndef REVOLUTION_CLIENT_H_
#define REVOLUTION_CLIENT_H_

#include <atomic>

#include "application.h"

namespace revolution {
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

#endif  // REVOLUTION_CLIENT_H_
