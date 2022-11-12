#ifndef REVOLUTION_SOLDIER_H
#define REVOLUTION_SOLDIER_H

#include "application.h"
#include "configuration.h"

namespace Revolution {
	class Soldier : public Application {
	public:
		explicit Soldier(
			const Header_space& header_space,
			const Key_space& key_space,
			const Topology& topology
		);
	protected:
		void set_state(
			const std::string& key,
			const std::string& value
		) override;

		std::vector<std::string> handle_write(
			const Messenger::Message& message
		) override;

		void add_handlers() override;

		void send_marshal(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		);
		Messenger::Message communicate_marshal(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		);
	};
}

#endif	// REVOLUTION_SOLDIER_H
