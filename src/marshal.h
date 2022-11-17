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
		const Topology::Endpoint& get_endpoint() const override;
		const Topology::Endpoint& get_syncer() const override;

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
	};
}

#endif	// REVOLUTION_MARSHAL_H
