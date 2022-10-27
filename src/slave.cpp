#include <functional>

#include "application.h"
#include "configuration.h"
#include "logger.h"
#include "messenger.h"
#include "slave.h"

namespace Revolution {
	Slave::Slave(
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
				&Slave::handle_set,
				this,
				std::placeholders::_1
			)
		);
	}

	void Slave::run()
	{
		get_messenger().send(
			get_topology().get_master().name,
			get_header_space().sync
		);

		Application::run();
	}

	void Slave::handle_set(const Messenger::Message& message)
	{
		Application::handle_set(message);

		if (message.sender_name != get_topology().get_master().name)
			get_messenger().send(
				get_topology().get_master().name,
				message.header,
				message.data
			);
	}
}
