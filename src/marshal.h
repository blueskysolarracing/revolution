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

		void handle_write(const Messenger::Message& message) override;

		void add_handlers() override;

		Messenger::Message communicate_with_soldiers(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		) const;
	};
}

#endif	// REVOLUTION_MARSHAL_H
