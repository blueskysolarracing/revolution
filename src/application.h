#ifndef REVOLUTION_APPLICATION_H
#define REVOLUTION_APPLICATION_H

#include "messenger.h"
#include "topology.h"

namespace Revolution {
	class Application {
	public:
		explicit Application(const Instance &instance);
		~Application();

		virtual void run() = 0;
	protected:
		const Instance &get_instance() const;
		Logger &get_logger();
		Messenger &get_messenger();
	private:
		const Instance instance;
		Logger logger;
		Messenger messenger;
	};
}

#endif	// REVOLUTION_APPLICATION_H
