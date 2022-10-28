#include <functional>

#include "application.h"
#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"
#include "soldier.h"

namespace Revolution {
	Soldier::Soldier(
		const Topology& topology,
		const Header_space& header_space,
		const Key_space& key_space,
		Logger& logger,
		const Messenger& messenger,
		Heart& heart
	) : Application{
		topology,
		header_space,
		key_space,
		logger,
		messenger,
		heart
	    }
	{
		set_handler(
			get_header_space().reset,
			std::bind(
				&Soldier::handle_write,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().set,
			std::bind(
				&Soldier::handle_write,
				this,
				std::placeholders::_1
			)
		);
	}

	void Soldier::run()
	{
		get_messenger().send(
			get_topology().get_marshal().name,
			get_header_space().sync
		);

		Application::run();
	}

	void Soldier::handle_write(const Messenger::Message& message)
	{
		if (message.sender_name == get_topology().get_marshal().name)
			Application::handle_write(message);
		else
			get_messenger().send(
				get_topology().get_marshal().name,
				message.header,
				message.data
			);
	}
}
