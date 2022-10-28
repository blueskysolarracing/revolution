#include <functional>

#include "application.h"
#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "marshal.h"
#include "messenger.h"

namespace Revolution {
	Marshal::Marshal(
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
				&Marshal::handle_set,
				this,
				std::placeholders::_1
			)
		);
	}

	void Marshal::run()
	{
		get_messenger().send(
			get_topology().replica.name,
			get_header_space().sync
		);

		Application::run();
	}

	void Marshal::handle_set(const Messenger::Message& message)
	{
		Application::handle_set(message);

		for (const auto& soldier : get_topology().get_soldiers())
			if (message.sender_name != soldier.name)
				get_messenger().send(
					soldier.name,
					message.header,
					message.data
				);
	}
}
