#ifndef REVOLUTION_REPLICA_H
#define REVOLUTION_REPLICA_H

#include <functional>

#include "configuration.h"
#include "soldier.h"

namespace Revolution {
	class Replica : public Soldier {
	public:
		explicit Replica(
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

#endif	// REVOLUTION_REPLICA_H

