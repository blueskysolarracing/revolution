#ifndef REVOLUTION_APP_H_
#define REVOLUTION_APP_H_

#include <functional>
#include <string>

#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/interprocess/ipc/message_queue.hpp>

namespace revolution {
class Message {
public:
	static Message deserialize(const std::string &rawMessage);

	explicit Message(const std::string &senderName, const std::string &content);

	const std::string &getSenderName() const;
	const std::string &getContent() const;

	std::string serialize() const;
private:
	std::string senderName_;
	std::string content_;
};

class App {
public:
	App(const std::string &name);
	~App();

	virtual void run() = 0;
protected:
	const std::string &getName() const;
	virtual unsigned int getPriority() const = 0;

	Message receive() const;
	Message tryReceive() const;
	Message timedReceive(const boost::posix_time::ptime &absTime) const;

	void send(const std::string &content, const std::string &recipientName) const;
private:
	static constexpr std::size_t maxMessageCount_ = 1000, maxMessageSize_ = 1000;

	Message helpReceive(
		std::function<std::string(boost::interprocess::message_queue &)> receiver
	) const;

	std::string name_;
};
}

#endif	// REVOLUTION_APP_H_
