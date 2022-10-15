#ifndef REVOLUTION_APP_H_
#define REVOLUTION_APP_H_

#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/interprocess/ipc/message_queue.hpp>
#include <functional>
#include <string>

namespace revolution {
class App {
public:
	App(std::string name);
	~App();

	virtual void run() = 0;
protected:
	std::string getName();
	virtual unsigned int getPriority() = 0;

	std::string receive();
	std::string tryReceive();
	std::string timedReceive(const boost::posix_time::ptime &absTime);

	void send(const std::string &message, const std::string &recipientName);
private:
	static constexpr std::size_t maxMessageCount_ = 1000, maxMessageSize_ = 1000;

	std::string helpReceive(std::function<std::string(boost::interprocess::message_queue &)> receiver);

	std::string name_;
};
}

#endif  // REVOLUTION_APP_H_
