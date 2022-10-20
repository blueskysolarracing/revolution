#ifndef REVOLUTION_MESSENGER_H
#define REVOLUTION_MESSENGER_H

#include <chrono>
#include <functional>
#include <optional>
#include <string>
#include <vector>

#include <mqueue.h>

namespace Revolution {
class Message {
public:
	static Message deserialize(const std::string &raw_message);

	explicit Message(
		const std::string &sender_name,
		const std::string &header_name,
		const std::vector<std::string> &arguments = {}
	);

	const std::string &get_sender_name() const;
	const std::string &get_header_name() const;
	const std::vector<std::string> &get_arguments() const;

	std::string serialize() const;
private:
	const std::string sender_name;
	const std::string header_name;
	const std::vector<std::string> arguments;
};

class Messenger {
public:
	explicit MessageQueue(const std::string &name);
	~MessageQueue();

	Message receive() ;
	std::optional<Message> timedReceive(
		const std::chrono::system_clock::time_point &timeout
	);

	void send(
		const std::string &recipientName,
		const std::string &typeName,
		const std::vector<std::string> &arguments = {}
	);
	bool timedSend(
		const std::chrono::system_clock::time_point &timeout,
		const std::string &recipientName,
		const std::string &typeName,
		const std::vector<std::string> &arguments = {}
	);
private:
	static const std::string namePrefix_;
	static const std::size_t maxMessageCount_, maxMessageSize_;
	static const int flags_, mode_;
	static const std::chrono::system_clock::duration defaultMessageTimeout_;
	static const unsigned int priority_;

	static const std::string &getNamePrefix();
	static const std::size_t &getMaxMessageCount();
	static const std::size_t &getMaxMessageSize();
	static const int getFlags();
	static const int getMode();
	static std::chrono::system_clock::time_point getDefaultMessageTimeout();
	static const unsigned int &getPriority();

	const std::string &getName();
	std::string getFullName();
	mqd_t &getDescriptor(const std::string &name);
	mq_attr &getAttributes(const std::string &name);

	std::optional<Message> helpReceive(
		std::function<ssize_t(mqd_t &, std::string &, unsigned int &)> receiver
	);

	bool helpSend(
		const std::string &recipientName,
		const std::string &typeName,
		const std::vector<std::string> &arguments,
		std::function<int(mqd_t &, const std::string &, unsigned int)> sender
	);

	const std::string name_;
	std::unordered_map<std::string, mqd_t> descriptors_;
	std::unordered_map<std::string, mq_attr> attributes_;
};
}

#endif	// REVOLUTION_MESSENGER_H
