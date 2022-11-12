#ifndef REVOLUTION_MARSHAL_H
#define REVOLUTION_MARSHAL_H

#include "application.h"
#include "configuration.h"

namespace Revolution {
	class Marshal : public Application {
	public:
		explicit Marshal(
			const Header_space& header_space,
			const Key_space& key_space,
			const Topology& topology
		);
	protected:
		const Topology::Endpoint& get_endpoint() const override;

		void broadcast(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		) const override;
		void broadcast(
			const Messenger::Message& message
		) const override;
		void send_soldiers(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		) const;
		void send_soldiers_except(
			const std::string& recipient_name,
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		) const;
		std::vector<Messenger::Message> communicate_soldiers(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		);
		std::vector<std::optional<Messenger::Message>>
			communicate_soldiers_except(
			const std::string& recipient_name,
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		);
	};
}

#endif	// REVOLUTION_MARSHAL_H
