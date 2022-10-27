#include <chrono>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <vector>

#include "configuration.h"
#include "logger.h"
#include "messenger.h"

int main(int argc, char *argv[])
{
	std::string name{"terminator"};
	Revolution::Topology topology;
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Logger logger{
		Revolution::Logger::Configuration{Revolution::Logger::warning}
	};
	Revolution::Messenger messenger{
		Revolution::Messenger::Configuration{name},
		logger
	};

	return 0;
}

