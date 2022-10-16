#include <iostream>

#include "app.h"

revolution::Message revolution::Message::deserialize(const std::string &rawMessage) {
  std::size_t index = rawMessage.find('\0');
  std::string senderName = rawMessage.substr(0, index),
    content = rawMessage.substr(index + 1);

  return Message{senderName, content};
}

revolution::Message::Message(const std::string &senderName, const std::string &content) : senderName_{senderName}, content_{content} {}

const std::string &revolution::Message::getSenderName() const {
  return senderName_;
}

const std::string &revolution::Message::getContent() const {
  return content_;
}

std::string revolution::Message::serialize() const {
  return getSenderName() + '\0' + getContent();
}

revolution::App::App(const std::string &name) : name_{name} {
  std::cout << "Starting " << getName() << "..." << std::endl;
}

revolution::App::~App() {
  boost::interprocess::message_queue::remove(getName().data());

  std::cout << "Exiting " << getName() << "..." << std::endl;
}

const std::string &revolution::App::getName() const {
  return name_;
}

revolution::Message revolution::App::receive() const {
  return helpReceive([this] (boost::interprocess::message_queue &messageQueue) {
    std::string rawMessage;
    boost::interprocess::message_queue::size_type receivedSize = 0;
    unsigned int priority;

    rawMessage.resize(maxMessageSize_);
    messageQueue.receive(
      rawMessage.data(),
      rawMessage.size(),
      receivedSize,
      priority
    );
    rawMessage.resize(receivedSize);

    return rawMessage;
  });
}

revolution::Message revolution::App::tryReceive() const {
  return helpReceive([this] (boost::interprocess::message_queue &messageQueue) {
    std::string rawMessage;
    boost::interprocess::message_queue::size_type receivedSize = 0;
    unsigned int priority;

    rawMessage.resize(maxMessageSize_);
    messageQueue.try_receive(
      rawMessage.data(),
      rawMessage.size(),
      receivedSize,
      priority
    );
    rawMessage.resize(receivedSize);

    return rawMessage;
  });
}

revolution::Message revolution::App::timedReceive(const boost::posix_time::ptime &absTime) const {
  return helpReceive([this, &absTime] (boost::interprocess::message_queue &messageQueue) {
    std::string rawMessage;
    boost::interprocess::message_queue::size_type receivedSize = 0;
    unsigned int priority;

    rawMessage.resize(maxMessageSize_);
    messageQueue.timed_receive(
      rawMessage.data(),
      rawMessage.size(),
      receivedSize,
      priority,
      absTime
    );
    rawMessage.resize(receivedSize);

    return rawMessage;
  });
}

void revolution::App::send(const std::string &content, const std::string &recipientName) const {
  Message message{getName(), content};
  std::string rawMessage = message.serialize();

  BOOST_TRY {
    boost::interprocess::message_queue messageQueue(
      boost::interprocess::open_or_create,
      recipientName.data(),
      maxMessageCount_,
      maxMessageSize_
    );
    messageQueue.send(rawMessage.data(), rawMessage.size(), getPriority());
  } BOOST_CATCH (boost::interprocess::interprocess_exception &exception) {
    std::cout << "ERROR: " << exception.what() << std::endl;
  } BOOST_CATCH_END
}

revolution::Message revolution::App::helpReceive(std::function<std::string(boost::interprocess::message_queue &)> receiver) const {
  std::string rawMessage;

  BOOST_TRY {
    boost::interprocess::message_queue messageQueue(
      boost::interprocess::open_or_create,
      getName().data(),
      maxMessageCount_,
      maxMessageSize_
    );
    rawMessage = receiver(messageQueue);
  } BOOST_CATCH (boost::interprocess::interprocess_exception &exception) {
    std::cout << "ERROR: " << exception.what() << std::endl;
  } BOOST_CATCH_END

  return Message::deserialize(rawMessage);
}
