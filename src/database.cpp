#include "database.h"

#include <atomic>
#include <cassert>
#include <functional>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	Database::Database(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const Key_space>& key_space,
		const std::reference_wrapper<const Topology>& topology,
		const Timeout& timeout
	) : Application{header_space, key_space, topology},
	    timeout{timeout},
	    states{},
	    state_mutex{} {}

	const std::string& Database::get_name() const {
		return get_topology().get_database();
	}

	void Database::setup() {
		Application::setup();

		set_handler(
			get_header_space().get_get(),
			std::bind(
				&Database::handle_get,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_set(),
			std::bind(
				&Database::handle_set,
				this,
				std::placeholders::_1
			)
		);

		get_worker_pool().work(std::bind(&Database::sync, this));
	}

	const Database::Timeout Database::default_timeout{
		std::chrono::seconds(1)
	};

	const Database::Timeout& Database::get_default_timeout() {
		return default_timeout;
	}

	const Database::Timeout& Database::get_timeout() const {
		return timeout;
	}

	const std::unordered_map<std::string, std::string>&
		Database::get_states() const {
		return states;
	}

	const std::mutex& Database::get_state_mutex() const {
		return state_mutex;
	}

	std::unordered_map<std::string, std::string>&
		Database::get_states() {
		return states;
	}

	std::mutex& Database::get_state_mutex() {
		return state_mutex;
	}

	std::vector<std::string> Database::get_state_data() {
		std::scoped_lock lock{get_state_mutex()};
		std::vector<std::string> state_data;

		get_logger() << Logger::Severity::information
			<< "Reading all key(s)..."
			<< std::endl;

		for (const auto& [key, value] : get_states()) {
			state_data.push_back(key);
			state_data.push_back(value);
		}

		return state_data;
	}
	
	void Database::set_state_data(
		const std::vector<std::string>& state_data
	) {
		assert(state_data.size() % 2 == 0);

		get_logger() << Logger::Severity::information
			<< "Writing "
			<< state_data.size() / 2
			<< " key(s)..."
			<< std::endl;

		for (std::size_t i{}; i + 1 < state_data.size(); i += 2)
			help_set_state(state_data[i], state_data[i + 1]);
	}

	std::optional<std::string> Database::help_get_state(const std::string& key) {
		std::scoped_lock lock{get_state_mutex()};

		if (!get_states().count(key))
			return std::nullopt;

		return get_states().at(key);
	}

	void Database::help_set_state(
		const std::string& key,
		const std::string& value
	) {
		{
			std::scoped_lock lock{get_state_mutex()};

			get_states()[key] = value;
		}

		// TODO: SEND KEY COMMANDS TO SOME APPLICATIONS
	}

	std::vector<std::string>
		Database::handle_get(const Messenger::Message& message) {
		if (message.get_data().size() != 1) {
			get_logger() << Logger::Severity::error
				<< "Get expects exactly one argument, but "
				<< message.get_data().size()
				<< " argument(s) were supplied. "
				<< "This message will be ignored."
				<< std::endl;

			return {};
		}

		std::string key = message.get_data().front();
		std::optional<std::string> value = help_get_state(key);

		if (!value) {
			get_logger() << Logger::Severity::information
				<< "The key: "
				<< key
				<< " does not exist."
				<< std::endl;

			return {};
		}

		return {value.value()};
	}

	std::vector<std::string> Database::handle_set(
		const Messenger::Message& message
	) {
		if (message.get_data().size() != 2) {
			get_logger() << Logger::Severity::error
				<< "Set expects exactly two arguments, but "
				<< message.get_data().size()
				<< " argument(s) were supplied. "
				<< "This message will be ignored."
				<< std::endl;

			return {};
		}

		std::string key = message.get_data().front();
		std::string value = message.get_data().back();

		help_set_state(key, value);

		return {};
	}

	void Database::sync() {
		get_logger() << Logger::Severity::information
			<< "Syncing with "
			<< get_topology().get_replica()
			<< "..."
			<< std::endl;

		auto message = communicate(
			get_topology().get_replica(),
			get_header_space().get_get()
		);

		set_state_data(message.get_data());

		while (get_status()) {
			send(
				get_topology().get_replica(),
				get_header_space().get_set(),
				get_state_data()
			);

			std::this_thread::sleep_for(get_timeout());
		}
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Topology topology;
	Revolution::Database database{header_space, key_space, topology};

	database.main();

	return 0;
}

