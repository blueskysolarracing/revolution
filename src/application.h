#ifndef REVOLUTION_APPLICATION_H
#define REVOLUTION_APPLICATION_H

#include "messenger.h"
#include "configuration.h"

namespace Revolution {
	class Application {
	public:
		explicit Application(const Instance &instance);
		~Application();

		void run();
	protected:
		const Instance &get_instance() const;
		Logger &get_logger();
		Messenger &get_messenger();

		virtual void handle(const Message &message) = 0;
	private:
		const Instance instance;
		Logger logger;
		Messenger messenger;
	};
}

#endif	// REVOLUTION_APPLICATION_H
