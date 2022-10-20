#include <iostream>
#include <sstream>

#include "message_queue.h"

namespace Revolution {
Message Message::deserialize(const std::string &raw_message)
{
	std::istringstream iss(raw_message);
	std::string sender_name;
	std::string header_name;
	std::string argument;
	std::vector<std::string> arguments;

	iss >> sender_name >> header_name;

	while (std::getline(iss, argument, '\0'))
		arguments.push_back(argument);

	return Message{sender_name, header_name, arguments};
}

Message::Message(
	const std::string &sender_name,
	const std::string &type_name,
	const std::vector<std::string> &arguments
) : sender_name{sender_name}, header_name{header_name}, arguments{arguments}
{
}

const std::string &Message::get_sender_name() const
{
	return sender_name;
}

const std::string &Message::get_header_name() const
{
	return header_name;
}

const std::vector<std::string> &Message::get_arguments() const
{
	return arguments;
}

std::string Message::serialize() const {
	std::ostringstream oss;

	oss << get_sender_name() << '\0' << get_header_name();

	for (const auto &argument : get_arguments())
		oss << '\0' << argument;

	return oss.str();
}

MessageQueue::MessageQueue(const std::string &name) : name_{name} {
}

MessageQueue::~MessageQueue() {
	for (auto p : descriptors_) {
		auto name = p.first;
		auto descriptor = p.second;
		auto fullName = getNamePrefix() + name;
		if (mq_close(descriptor) == (mqd_t) - 1)
			std::cout << "ERROR ON CLOSE" << std::endl;
	}
}

Message MessageQueue::receive() {
	return helpReceive([] (
		mqd_t &descriptor,
		std::string &rawMessage,
		unsigned int &priority
		) {
		return mq_receive(
			descriptor,
			rawMessage.data(),
			rawMessage.size(),
			&priority
		);
	}).value();
}

std::optional<Message> MessageQueue::timedReceive(
	const std::chrono::system_clock::time_point &timeout
) {
	auto duration = timeout.time_since_epoch();
	auto seconds = std::chrono::duration_cast<std::chrono::seconds>(duration);
	auto nanoseconds = std::chrono::duration_cast<std::chrono::nanoseconds>(duration - seconds);
	timespec absTimeout{seconds.count(), nanoseconds.count()};

	return helpReceive([&] (
		mqd_t &descriptor,
		std::string &rawMessage,
		unsigned int &priority
	) {
		return mq_timedreceive(
			descriptor,
			rawMessage.data(),
			rawMessage.size(),
			&priority,
			&absTimeout
		);
	});
}

void MessageQueue::send(
	const std::string &recipientName,
	const std::string &typeName,
	const std::vector<std::string> &arguments
) {
	helpSend(recipientName, typeName, arguments, [] (
		mqd_t &descriptor,
		const std::string &rawMessage,
		unsigned int priority
	) {
		return mq_send(
			descriptor,
			rawMessage.data(),
			rawMessage.size(),
			priority
		);
	});
}

bool MessageQueue::timedSend(
	const std::chrono::system_clock::time_point &timeout,
	const std::string &recipientName,
	const std::string &typeName,
	const std::vector<std::string> &arguments
) {
	auto duration = timeout.time_since_epoch();
	auto seconds = std::chrono::duration_cast<std::chrono::seconds>(duration);
	auto nanoseconds = std::chrono::duration_cast<std::chrono::nanoseconds>(duration - seconds);
	timespec absTimeout{seconds.count(), nanoseconds.count()};

	return helpSend(recipientName, typeName, arguments, [&] (
		mqd_t &descriptor,
		const std::string &rawMessage,
		unsigned int priority
	) {
		return mq_timedsend(
			descriptor,
			rawMessage.data(),
			rawMessage.size(),
			priority,
			&absTimeout
		);
	});
}

const std::string MessageQueue::namePrefix_ = "/revolution_";
const std::size_t MessageQueue::maxMessageCount_ = 8,
			MessageQueue::maxMessageSize_ = 1024;
const int MessageQueue::flags_ = O_RDWR | O_CREAT,
			MessageQueue::mode_ = 0644;
const std::chrono::system_clock::duration MessageQueue::defaultMessageTimeout_
	= std::chrono::milliseconds(100);
const unsigned int MessageQueue::priority_ = 0;

const std::string &MessageQueue::getNamePrefix() { return namePrefix_; }

const std::size_t &MessageQueue::getMaxMessageCount() {
	return maxMessageCount_;
}

const std::size_t &MessageQueue::getMaxMessageSize() {
	return maxMessageSize_;
}

const int MessageQueue::getFlags() { return flags_; };
const int MessageQueue::getMode() { return mode_; };

std::chrono::system_clock::time_point MessageQueue::getDefaultMessageTimeout() {
	return std::chrono::system_clock::now() + defaultMessageTimeout_;
}

const unsigned int &MessageQueue::getPriority() { return priority_; }

const std::string &MessageQueue::getName() {
	return name_;
}

mqd_t &MessageQueue::getDescriptor(const std::string &name) {
	if (descriptors_.count(name))
		return descriptors_[name];

	std::string fullName = getNamePrefix() + name;
	descriptors_[name] = mq_open(
		fullName.data(),
		getFlags(),
		getMode(),
		&getAttributes(name)
	);

	if (descriptors_[name] == (mqd_t) - 1)
		std::cout << "ERROR ON CREATION" << std::endl;
	return descriptors_[name];
}

mq_attr &MessageQueue::getAttributes(const std::string &name) {
	if (attributes_.count(name))
		return attributes_[name];
	attributes_[name].mq_flags = 0;
	attributes_[name].mq_maxmsg = getMaxMessageCount();
	attributes_[name].mq_msgsize = getMaxMessageSize();
	attributes_[name].mq_curmsgs = 0;

	return attributes_[name];
}

std::optional<Message> MessageQueue::helpReceive(
		std::function<ssize_t(mqd_t &, std::string &, unsigned int &)> receiver
) {
	std::string rawMessage;
	rawMessage.resize(getMaxMessageSize());
	ssize_t receivedSize;
	unsigned int priority;

	receivedSize = receiver(getDescriptor(getName()), rawMessage, priority);

	if (receivedSize == -1)
		return std::nullopt;

	rawMessage.resize(receivedSize);

	return Message::deserialize(rawMessage);
}

bool MessageQueue::helpSend(
		const std::string &recipientName,
		const std::string &typeName,
		const std::vector<std::string> &arguments,
		std::function<int(mqd_t &, const std::string &, unsigned int)> sender
) {
	Message message{getName(), typeName, arguments};
	std::string rawMessage{message.serialize()};

	int result = sender(
		getDescriptor(recipientName), rawMessage, getPriority());

	return result != -1;
}
}
