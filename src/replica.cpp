#include "replica.h"

#include <functional>
#include <mutex>
#include <string>
#include <vector>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	Replica::Replica(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const Key_space>& key_space,
		const std::reference_wrapper<const Topology>& topology
	) : Application{
		header_space,
		key_space,
		topology,
		topology.get().get_replica()
	    },
	    state_data{} {}

	void Replica::setup() {
		Application::setup();

		set_handler(
			get_header_space().get_get(),
			std::bind(
				&Replica::handle_get,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_set(),
			std::bind(
				&Replica::handle_set,
				this,
				std::placeholders::_1
			)
		);
	}

	const std::vector<std::string>& Replica::get_state_data() const {
		return state_data;
	}

	const std::mutex& Replica::get_state_data_mutex() const {
		return state_data_mutex;
	}

	std::vector<std::string>& Replica::get_state_data() {
		return state_data;
	}

	std::mutex& Replica::get_state_data_mutex() {
		return state_data_mutex;
	}

	std::vector<std::string>
		Replica::handle_get(const Messenger::Message& message) {
		if (!message.get_data().empty()) {
			get_logger() << Logger::Severity::error
				<< "Get expects no argument, but "
				<< message.get_data().size()
				<< " argument(s) were supplied. "
				<< "This message will be ignored."
				<< std::endl;

			return {};
		}

		std::scoped_lock lock{get_state_data_mutex()};

		return get_state_data();
	}

	std::vector<std::string> Replica::handle_set(
		const Messenger::Message& message
	) {
		if (message.get_data().size() % 2 != 0) {
			get_logger() << Logger::Severity::error
				<< "Set expects 2 * n arguments, but "
				<< message.get_data().size()
				<< " argument(s) were supplied. "
				<< "This message will be ignored."
				<< std::endl;

			return {};
		}

		std::scoped_lock lock{get_state_data_mutex()};

		get_state_data() = message.get_data();

		return {};
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Topology topology;
	Revolution::Replica replica{header_space, key_space, topology};

	replica.main();

	return 0;
}
