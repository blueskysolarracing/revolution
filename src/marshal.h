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
		void set_state(
			const std::string& key,
			const std::string& value
		) override;
		const Topology::Endpoint& get_endpoint() const override;

		std::vector<std::string> handle_write(
			const Messenger::Message& message
		) override;

		void add_handlers() override;

		void send_soldiers(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		);
		void send_soldiers_except(
			const std::string& recipient_name,
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		);
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
