#ifndef REVOLUTION_SLAVE_H_
#define REVOLUTION_SLAVE_H_

#include "app.h"

namespace revolution {
class Slave : public App {
public:
	Slave(std::string name);
	~Slave();
protected:
	void sendMaster(std::string message) const;
};
}

#endif  // REVOLUTION_SLAVE_H_
