#ifndef REVOLUTION_CLIENT_H
#define REVOLUTION_CLIENT_H

#include "application.h"

namespace Revolution {
	class Client : public Application {
	public:
		explicit Client(
			const std::string &sender_name,
			const std::string &recipient_name
		);

		void run() override;
	private:
		static const unsigned int priority;
		static const Log_level log_level;
		static const std::string log_filename;

		static const unsigned int &get_priority();
		static const Log_level &get_log_level();
		static const std::string &get_log_filename();
		static const std::string get_command(std::string sender_name, std::string recipient_name);

		const std::string &get_recipient_name() const;

		void help_run();

		std::string recipient_name;
	};
}

#endif	// REVOLUTION_CLIENT_H
