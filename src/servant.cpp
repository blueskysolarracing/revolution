#include <functional>

#include "application.h"
#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"
#include "servant.h"

namespace Revolution {
	Servant::Servant(
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
			get_header_space().set,
			std::bind(
				&Servant::handle_set,
				this,
				std::placeholders::_1
			)
		);
	}

	void Servant::run()
	{
		get_messenger().send(
			get_topology().get_master().name,
			get_header_space().sync
		);

		Application::run();
	}

	void Servant::handle_set(const Messenger::Message& message)
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
