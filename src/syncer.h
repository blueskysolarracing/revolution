#ifndef REVOLUTION_SYNCER_H_
#define REVOLUTION_SYNCER_H_

#include <unordered_map>

#include "application.h"
#include "topology.h"

namespace revolution {
class Commands;
class Syncer : public Application {
public:
  Syncer();

  void run() override;
private:
  void broadcast(const std::string &typeName, const std::vector<std::string> &arguments = {});
  void broadcastState();
  void sendState(const std::string &slaveName);

  std::unordered_map<std::string, std::string> state_;
  bool exit_;

  friend Commands;
};

class Commands {
public:
  static void execute(
    Syncer &syncer,
    const std::string &senderName,
    const std::string &commandName,
    const std::vector<std::string> &arguments
  );
private:
  static std::unordered_map<
    std::string,
    std::function<
      void(
        Syncer &syncer,
        const std::string &senderName,
        const std::vector<std::string> &arguments
      )
    >
  > commands_;

  static void get(
    Syncer &syncer,
    const std::string &senderName,
    const std::vector<std::string> &arguments
  );

  static void set(
    Syncer &syncer,
    const std::string &senderName,
    const std::vector<std::string> &arguments
  );

  static void exit(
    Syncer &syncer,
    const std::string &senderName,
    const std::vector<std::string> &arguments
  );
};
}

#endif  // REVOLUTION_SYNCER_H_
