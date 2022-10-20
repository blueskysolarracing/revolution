#include "syncer.h"

namespace revolution {
Syncer::Syncer() : Application{Top} {
}

void Syncer::run() {
  for (;;) {
    boost::posix_time::ptime absTime = boost::posix_time::microsec_clock::local_time() + pollingPeriod;
    revolution::Message message = timedReceive(absTime);

    if (!message.getContent().empty()) {
      boost::json::value command = 
    }
  }
}

unsigned int Syncer::getPriority() const {
  return priority_;
}

const std::vector<std::string> &Syncer::getSlaveNames() {
  return slaveNames_;
}

void Syncer::resetSlaves() {
  for (const std::string &slaveName : getSlaveNames()) {
    BOOST_TRY {
      boost::interprocess::message_queue::remove(slaveName.data());
    } BOOST_CATCH (boost::interprocess::interprocess_exception &exception) {
      std::cout << "Failure: " << exception.what() << std::endl;
    } BOOST_CATCH_END
  }
}

void Syncer::sendSlaves(const std::string &message) {
  for (const std::string &slaveName : getSlaveNames())
    send(message, slaveName);
}

void Commands::execute(
  Syncer &syncer,
  const std::string &senderName,
  const std::string &commandName,
  const boost::json::value &arguments
) {
  if (commands_.count(commandName))
    commands_[commandName](syncer, senderName, arguments);
}

std::unordered_map<
  std::string,
  std::function<
    void(
      Syncer &syncer,
      const std::string &senderName,
      const boost::json::value &arguments
    )
  >
> Commands::commands_ {  // TODO
  {"GET", Commands::get},
  {"SET", Commands::set},
  {"UPDATE", Commands::update}
};

void Commands::get(
  Syncer &syncer,
  const std::string &senderName,
  const boost::json::value &arguments
) {
  std::cout << "get" << std::endl;
}

void Commands::set(
  Syncer &syncer,
  const std::string &senderName,
  const boost::json::value &arguments
) {
  std::cout << "set" << std::endl;
}

void Commands::update(
  Syncer &syncer,
  const std::string &senderName,
  const boost::json::value &arguments
) {
  std::cout << "update" << std::endl;
}
}

int main() {
  revolution::Syncer &syncer = revolution::Syncer::getInstance();

  syncer.run();

  return 0;
}
