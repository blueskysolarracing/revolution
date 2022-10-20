#ifndef REVOLUTION_TELEMETER_H
#define REVOLUTION_TELEMETER_H

#include "slave.h"

namespace revolution {
class Telemeter : public Slave {
public:
  static Telemeter &getInstance() {
    static Telemeter telemeter;

    return telemeter;
  }

  void run() override;
protected:
  unsigned int getPriority() const override;
private:
  static constexpr unsigned int priority_ = 0;

  Telemeter();
  Telemeter(Telemeter const &) = delete;

  void operator=(Telemeter const &) = delete;
};
}

#endif  // REVOLUTION_TELEMETER_H
