#ifndef REVOLUTION_MARSHAL_H
#define REVOLUTION_MARSHAL_H

#include <functional>
#include <string>
#include <vector>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	class Marshal : public Application {
	public:
		explicit Marshal(
			const std::reference_wrapper<const Header_space>&
				header_space,
			const std::reference_wrapper<const Key_space>&
				key_space,
			const std::reference_wrapper<const Topology>& topology
		);
	protected:
		void help_set_state(
			const std::string& key,
			const std::string& value
		) override;
		const Topology::Endpoint& get_endpoint() const override;
		const Topology::Endpoint& get_syncer() const override;

		std::vector<std::string> help_handle_write(
			const Messenger::Message& message
		) override;

		std::vector<Messenger::Message> communicate_soldiers(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		);
	};
}

#endif	// REVOLUTION_MARSHAL_H
