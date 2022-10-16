#ifndef REVOLUTION_DISPLAY_DRIVER_H_
#define REVOLUTION_DISPLAY_DRIVER_H_

#include "slave.h"

namespace revolution {
class DisplayDriver : public Slave {
public:
	static DisplayDriver &getInstance() {
		static DisplayDriver displayDriver;

		return displayDriver;
	}

	void run() override;
protected:
	unsigned int getPriority() const override;
private:
	static constexpr unsigned int priority_ = 0;

	DisplayDriver();
	DisplayDriver(DisplayDriver const &) = delete;

	void operator=(DisplayDriver const &) = delete;
};
}

#endif  // REVOLUTION_DISPLAY_DRIVER_H_
