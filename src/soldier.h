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
		void broadcast(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		) const override;
		void broadcast(
			const Messenger::Message& message
		) const override;
		void send_marshal(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		) const;
		Messenger::Message communicate_marshal(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		);
	};
}

#endif	// REVOLUTION_SOLDIER_H
