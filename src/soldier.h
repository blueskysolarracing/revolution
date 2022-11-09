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

		void run() override;
	protected:
		const Topology::Endpoint& get_endpoint() const override;

		void handle_write(const Messenger::Message& message) override;

		void add_handlers() override;

		Messenger::Message communicate_with_marshal(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		) const;
	};
}

#endif	// REVOLUTION_SOLDIER_H
