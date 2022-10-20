#ifndef REVOLUTION_VOLTAGE_CONTROLLER_H
#define REVOLUTION_VOLTAGE_CONTROLLER_H

#include "slave.h"

namespace revolution {
class VoltageController : public Slave {
public:
  static VoltageController &getInstance() {
    static VoltageController voltageController;

    return voltageController;
  }

  void run() override;
protected:
  unsigned int getPriority() const override;
private:
  static constexpr unsigned int priority_ = 0;

  VoltageController();
  VoltageController(VoltageController const &) = delete;

  void operator=(VoltageController const &) = delete;
};
}

#endif  // REVOLUTION_VOLTAGE_CONTROLLER_H
