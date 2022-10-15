#ifndef REVOLUTION_ECHO_H_
#define REVOLUTION_ECHO_H_

#include "app.h"

namespace revolution {
class Echo : public App {
public:
	static Echo &getInstance() {
		static Echo echo;

		return echo;
	}

	void run() override;
protected:
	unsigned int getPriority() override;
private:
	static constexpr unsigned int priority_ = 0;
	static constexpr boost::posix_time::time_duration pollingPeriod = boost::posix_time::milliseconds(100);

	Echo();
	Echo(Echo const &) = delete;

	void operator=(Echo const &) = delete;
};
}

#endif  // REVOLUTION_ECHO_H_
