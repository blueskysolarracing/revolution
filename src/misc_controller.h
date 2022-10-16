#ifndef REVOLUTION_MISC_CONTROLLER_H_
#define REVOLUTION_MISC_CONTROLLER_H_

#include "slave.h"

namespace revolution {
class MiscController : public Slave {
public:
  static MiscController &getInstance() {
    static MiscController miscController;

    return miscController;
  }

  void run() override;
protected:
  unsigned int getPriority() const override;
private:
  static constexpr unsigned int priority_ = 0;

  MiscController();
  MiscController(MiscController const &) = delete;

  void operator=(MiscController const &) = delete;
};
}

#endif  // REVOLUTION_MISC_CONTROLLER_H_
