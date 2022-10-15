#ifndef REVOLUTION_MOTOR_CONTROLLER_H_
#define REVOLUTION_MOTOR_CONTROLLER_H_

#include "slave.h"

namespace revolution {
class MotorController : public Slave {
public:
	static MotorController &getInstance() {
		static MotorController motorController;

		return motorController;
	}

	void run() override;
protected:
	unsigned int getPriority() override;
private:
	static constexpr unsigned int priority_ = 0;

	MotorController();
	MotorController(MotorController const &) = delete;

	void operator=(MotorController const &) = delete;
};
}

#endif  // REVOLUTION_MOTOR_CONTROLLER_H_
