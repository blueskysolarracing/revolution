#include "topology.h"

namespace revolution {
const revolution::Topology::Instance Topology::master {
	"syncer"
};

const std::vector<revolution::Topology::Instance> Topology::slaves {
	{
		"display_driver"
	},
	{
		"miscellanious_controller"
	},
	{
		"motor_controller"
	},
	{
		"power_sensor"
	},
	{
		"telemeter"
	},
	{
		"voltage_controller"
	}
};
}
