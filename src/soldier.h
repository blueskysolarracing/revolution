#ifndef REVOLUTION_SOLDIER_H
#define REVOLUTION_SOLDIER_H

#include <functional>
#include <string>
#include <vector>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	class Soldier : public Application {
	public:
		explicit Soldier(
			const std::reference_wrapper<const Header_space>&
				header_space,
			const std::reference_wrapper<const Key_space>&
				key_space,
			const std::reference_wrapper<const Topology>& topology
		);
	protected:
		const Topology::Endpoint& get_syncer() const override;

		void broadcast(
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		) const override;
		void broadcast(
			const Messenger::Message& message
		) const override;
		Messenger::Message send_marshal(
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
