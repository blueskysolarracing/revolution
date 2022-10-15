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

	Echo();
	Echo(Echo const &) = delete;

	void operator=(Echo const &) = delete;
};
}

#endif  // REVOLUTION_ECHO_H_
