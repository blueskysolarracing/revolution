#include "marshal.h"

#include <functional>

#include "application.h"
#include "configuration.h"
#include "logger.h"
#include "messenger.h"

namespace Revolution {
	Marshal::Marshal(
		const Header_space& header_space,
		const Key_space& key_space,
		const Topology& topology
	) : Application{header_space, key_space, topology} {}

	{
		set_handler(
			get_header_space().reset,
			std::bind(
				&Marshal::handle_write,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().set,
			std::bind(
				&Marshal::handle_write,
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

	void Marshal::handle_write(const Messenger::Message& message)
	{
		Application::handle_write(message);

		for (const auto& soldier : get_topology().get_soldiers())
			get_messenger().send(
				soldier.name,
				message.header,
				message.data
			);
	}
}
