#ifndef REVOLUTION_SYNCER_H_
#define REVOLUTION_SYNCER_H_

#include <unordered_map>

#include "application.h"
#include "topology.h"

namespace revolution {
class Syncer : public App {
public:
  Syncer();

  void run() override;
protected:
  unsigned int getPriority() const override;
private:
  static constexpr unsigned int priority_ = 0;
  static const std::vector<std::string> slaveNames_;
  static constexpr boost::posix_time::time_duration pollingPeriod = boost::posix_time::milliseconds(100);

  Syncer();
  Syncer(Syncer const &) = delete;

  void operator=(Syncer const &) = delete;

  const std::vector<std::string> &getSlaveNames();
  void resetSlaves();
  void sendSlaves(const std::string &message);

  boost::json::value state;
};

class Commands {
public:
  static void execute(
    Syncer &syncer,
    const std::string &senderName,
    const std::string &commandName,
    const boost::json::value &arguments
  );
private:
  static std::unordered_map<
    std::string,
    std::function<
      void(
        Syncer &syncer,
        const std::string &senderName,
        const boost::json::value &arguments
      )
    >
  > commands_;

  static void get(
    Syncer &syncer,
    const std::string &senderName,
    const boost::json::value &arguments
  );

  static void set(
    Syncer &syncer,
    const std::string &senderName,
    const boost::json::value &arguments
  );

  static void update(
    Syncer &syncer,
    const std::string &senderName,
    const boost::json::value &arguments
  );

  friend Syncer;
};
}

#endif  // REVOLUTION_SYNCER_H_
