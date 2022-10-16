#ifndef REVOLUTION_APP_H_
#define REVOLUTION_APP_H_

#include <functional>
#include <string>

#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/interprocess/ipc/message_queue.hpp>

namespace revolution {
class App {
public:
	App(std::string name);
	~App();

	virtual void run() = 0;
protected:
	const std::string &getName() const;
	virtual unsigned int getPriority() const = 0;

	std::string receive() const;
	std::string tryReceive() const;
	std::string timedReceive(const boost::posix_time::ptime &absTime) const;

	void send(const std::string &message, const std::string &recipientName) const;
private:
	static constexpr std::size_t maxMessageCount_ = 1000, maxMessageSize_ = 1000;

	std::string helpReceive(std::function<std::string(boost::interprocess::message_queue &)> receiver) const;

	std::string name_;
};
}

#endif  // REVOLUTION_APP_H_
