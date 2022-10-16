#ifndef REVOLUTION_SLAVE_H_
#define REVOLUTION_SLAVE_H_

#include "app.h"

namespace revolution {
class Slave : public App {
public:
	Slave(const std::string &name);
	~Slave();
protected:
	void sendMaster(const std::string &message) const;
};
}

#endif  // REVOLUTION_SLAVE_H_
