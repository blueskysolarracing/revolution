#ifndef REVOLUTION_CLIENT_H_
#define REVOLUTION_CLIENT_H_

#include <atomic>

#include "app.h"

namespace revolution {
class Client : public App {
public:
	static Client &getInstance() {
		static Client client;

		return client;
	}

	void run() override;
protected:
	unsigned int getPriority() override;
private:
	static constexpr unsigned int priority_ = 0;
	static constexpr boost::posix_time::time_duration pollingPeriod = boost::posix_time::milliseconds(100);

	Client();
	Client(Client const &) = delete;

	void operator=(Client const &) = delete;

	void helpRun();

	std::atomic_bool exit_;
};
}

#endif  // REVOLUTION_CLIENT_H_
