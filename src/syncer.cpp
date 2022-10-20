#include "syncer.h"

namespace revolution {
Syncer::Syncer() : Application{Topology::master.name}, exit_{false} {
  std::string temp;

  for (const auto& slave: Topology::slaves) {
    temp = "/revolution_" + slave.name;
    mq_unlink(temp.data());
  }
}

void Syncer::run() {
  while (!exit_) {
    Message message = getMessageQueue().receive();

    Commands::execute(*this, message.getSenderName(), message.getTypeName(), message.getArguments());
  }
}

void Syncer::broadcast(const std::string &typeName, const std::vector<std::string> &arguments) {
  for (const auto& slave: Topology::slaves)
    getMessageQueue().send(slave.name, typeName, arguments);
}

void Syncer::broadcastState() {
  std::vector<std::string> arguments;

  for (auto &p : state_)
    arguments.push_back(p.first), arguments.push_back(p.second);

  broadcast("STATE", arguments);
}

void Syncer::sendState(const std::string &slaveName) {
  std::vector<std::string> arguments;

  for (auto &p : state_)
    arguments.push_back(p.first), arguments.push_back(p.second);

  getMessageQueue().send(slaveName, "STATE", arguments);
}

void Commands::execute(
  Syncer &syncer,
  const std::string &senderName,
  const std::string &commandName,
  const std::vector<std::string> &arguments
) {
  if (commands_.count(commandName))
    commands_[commandName](syncer, senderName, arguments);
  else
    std::cout << commandName << " not found!" << std::endl;
}

std::unordered_map<
  std::string,
  std::function<
    void(
      Syncer &syncer,
      const std::string &senderName,
      const std::vector<std::string> &arguments
    )
  >
> Commands::commands_ {  // TODO
  {"GET", Commands::get},
  {"SET", Commands::set},
  {"EXIT", Commands::exit}
};

void Commands::get(
  Syncer &syncer,
  const std::string &senderName,
  const std::vector<std::string> &arguments
) {
  syncer.sendState(senderName);
}

void Commands::set(
  Syncer &syncer,
  const std::string &senderName,
  const std::vector<std::string> &arguments
) {
  for (int i = 0; i < arguments.size(); i += 2)
    syncer.state_[arguments[i]] = arguments[i + 1];

  syncer.broadcastState();
}

void Commands::exit(
  Syncer &syncer,
  const std::string &senderName,
  const std::vector<std::string> &arguments
) {
  syncer.exit_ = true;
  syncer.broadcast("EXIT");
}
}

int main() {
  revolution::Syncer syncer;

  syncer.run();

  return 0;
}
