#include <functional>

#include "application.h"
#include "configuration.h"
#include "logger.h"
#include "master.h"
#include "messenger.h"

namespace Revolution {
	Master::Master(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		Logger& logger,
		const Messenger& messenger
	) : Application{topology, header_space, key_space, logger, messenger}
	{
		set_handler(
			get_header_space().set,
			std::bind(
				&Master::handle_set,
				this,
				std::placeholders::_1
			)
		);
	}

	void Master::run()
	{
		get_messenger().send(
			get_topology().replica.name,
			get_header_space().sync
		);

		Application::run();
	}

	void Master::handle_set(const Messenger::Message& message)
	{
		Application::handle_set(message);

		for (const auto& slave : get_topology().get_slaves())
			if (message.sender_name != slave.name)
				get_messenger().send(
					slave.name,
					message.header,
					message.data
				);
	}
}
