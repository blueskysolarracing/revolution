#ifndef REVOLUTION_TELEMETER_H
#define REVOLUTION_TELEMETER_H

#include <functional>

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	class Telemeter : public Soldier {
	public:
		explicit Telemeter(
			const std::reference_wrapper<const Header_space>&
				header_space,
			const std::reference_wrapper<const Key_space>&
				key_space,
			const std::reference_wrapper<const Topology>& topology
		);
	protected:
		const Topology::Endpoint& get_endpoint() const override;
	};
}

#endif	// REVOLUTION_TELEMETER_H

