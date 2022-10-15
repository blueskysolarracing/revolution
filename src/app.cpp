#include <iostream>

#include "app.h"

revolution::App::App(std::string name) : name_{name} {
	std::cout << "Starting " << getName() << "..." << std::endl;
}

revolution::App::~App() {
	boost::interprocess::message_queue::remove(getName().data());

	std::cout << "Exiting " << getName() << "..." << std::endl;
}

std::string revolution::App::getName() {
	return name_;
}

std::string revolution::App::receive() {
	return helpReceive([this] (boost::interprocess::message_queue &messageQueue) -> std::string {
		std::string message;
		boost::interprocess::message_queue::size_type receivedSize;
		unsigned int priority;

		message.resize(maxMessageSize_);
		messageQueue.receive(
			message.data(),
			message.size(),
			receivedSize,
			priority
		);
		message.resize(receivedSize);

		return message;
	});
}

std::string revolution::App::tryReceive() {
	return helpReceive([this] (boost::interprocess::message_queue &messageQueue) -> std::string {
		std::string message;
		boost::interprocess::message_queue::size_type receivedSize;
		unsigned int priority;

		message.resize(maxMessageSize_);
		messageQueue.try_receive(
			message.data(),
			message.size(),
			receivedSize,
			priority
		);
		message.resize(receivedSize);

		return message;
	});
}

std::string revolution::App::timedReceive(const boost::posix_time::ptime &absTime) {
	return helpReceive([this, &absTime] (boost::interprocess::message_queue &messageQueue) -> std::string {
		std::string message;
		boost::interprocess::message_queue::size_type receivedSize;
		unsigned int priority;

		message.resize(maxMessageSize_);
		messageQueue.timed_receive(
			message.data(),
			message.size(),
			receivedSize,
			priority,
			absTime
		);
		message.resize(receivedSize);

		return message;
	});
}

void revolution::App::send(const std::string &message, const std::string &recipientName) {
	BOOST_TRY {
		boost::interprocess::message_queue messageQueue(
			boost::interprocess::open_or_create,
			recipientName.data(),
			maxMessageCount_,
			maxMessageSize_
		);
		messageQueue.send(message.data(), message.size(), getPriority());

		std::cout << "Sent message: " << message << std::endl;
	} BOOST_CATCH (boost::interprocess::interprocess_exception &exception) {
		std::cout << "ERROR: " << exception.what() << std::endl;
	} BOOST_CATCH_END
}

std::string revolution::App::helpReceive(std::function<std::string(boost::interprocess::message_queue &)> receiver) {
	std::string message;

	BOOST_TRY {
		boost::interprocess::message_queue messageQueue(
			boost::interprocess::open_or_create,
			getName().data(),
			maxMessageCount_,
			maxMessageSize_
		);
		message = receiver(messageQueue);

		std::cout << "Received message: " << message << std::endl;
	} BOOST_CATCH (boost::interprocess::interprocess_exception &exception) {
		std::cout << "ERROR: " << exception.what() << std::endl;
	} BOOST_CATCH_END

	return message;
}
