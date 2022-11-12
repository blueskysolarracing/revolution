#ifndef REVOLUTION_TELEMETER_H
#define REVOLUTION_TELEMETER_H

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	class Telemeter : public Soldier {
	public:
		explicit Telemeter(
			const Header_space& header_space,
			const Key_space& key_space,
			const Topology& topology
		);
	protected:
		const Topology::Endpoint& get_endpoint() const override;
	};
}

#endif	// REVOLUTION_TELEMETER_H

