#include "topology.h"

namespace revolution {
Instance Topology::master {
	"syncer"
};

std::vector<Instance> Topology::slaves {
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
