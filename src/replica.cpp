#include "replica.h"

#include <functional>
#include <mutex>
#include <ostream>
#include <string>
#include <vector>

#include "application.h"
#include "configuration.h"
#include "logger.h"
#include "messenger.h"

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
	    data{} {}

	void Replica::setup() {
		Application::setup();

		set_handler(
			get_header_space().get_data(),
			std::bind(
				&Replica::handle_data,
				this,
				std::placeholders::_1
			)
		);
	}

	const std::vector<std::string>& Replica::get_data() const {
		return data;
	}

	const std::mutex& Replica::get_data_mutex() const {
		return data_mutex;
	}

	std::vector<std::string>& Replica::get_data() {
		return data;
	}

	std::mutex& Replica::get_data_mutex() {
		return data_mutex;
	}

	std::vector<std::string>
		Replica::handle_data(const Messenger::Message& message) {
		std::scoped_lock lock{get_data_mutex()};

		if (message.get_data().empty()) {
			get_logger() << Logger::Severity::information
				<< "Retrieving data..."
				<< std::endl;

			return get_data();
		} else if (message.get_data().size() % 2 == 0) {
			get_logger() << Logger::Severity::information
				<< "Storing data..."
				<< std::endl;

			get_data() = message.get_data();

			return {};
		}

		get_logger() << Logger::Severity::error
			<< "Data expects 2 * n arguments (n >= 0), but "
			<< message.get_data().size()
			<< " argument(s) were supplied. "
			<< "This message will be ignored."
			<< std::endl;

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
