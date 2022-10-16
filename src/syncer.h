#ifndef REVOLUTION_SYNCER_H_
#define REVOLUTION_SYNCER_H_

#include "app.h"

namespace revolution {
class Syncer : public App {
public:
  static Syncer &getInstance() {
    static Syncer syncer;

    return syncer;
  }

  void run() override;
protected:
  unsigned int getPriority() const override;
private:
  static constexpr unsigned int priority_ = 0;

  Syncer();
  Syncer(Syncer const &) = delete;

  void operator=(Syncer const &) = delete;
};
}

#endif  // REVOLUTION_SYNCER_H_
