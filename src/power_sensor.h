#ifndef REVOLUTION_POWER_SENSOR_H_
#define REVOLUTION_POWER_SENSOR_H_

#include "slave.h"

namespace revolution {
class PowerSensor : public Slave {
public:
	static PowerSensor &getInstance() {
		static PowerSensor powerSensor;

		return powerSensor;
	}

	void run() override;
protected:
	unsigned int getPriority() const override;
private:
	static constexpr unsigned int priority_ = 0;

	PowerSensor();
	PowerSensor(PowerSensor const &) = delete;

	void operator=(PowerSensor const &) = delete;
};
}

#endif  // REVOLUTION_POWER_SENSOR_H_
