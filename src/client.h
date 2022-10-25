#ifndef REVOLUTION_CLIENT_H
#define REVOLUTION_CLIENT_H

#include "application.h"

namespace Revolution {
	class Client : public Application {
	public:
		explicit Client(
			const std::string& name,
			const Logger::Configuration& logger_configuration,
			const Messenger::Configuration& messenger_configuration,
			const std::string& recipient_name
		);

		void run() override;
	private:
		const std::string& get_recipient_name() const;

		void help_run();

		std::string recipient_name;
	};
}

#endif	// REVOLUTION_CLIENT_H
