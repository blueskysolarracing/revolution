#include "database.h"

#include <atomic>
#include <chrono>
#include <functional>
#include <limits>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

#include "application.h"
#include "configuration.h"
#include "logger.h"
#include "messenger.h"

namespace Revolution {
	Database::Database(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const State_space>& state_space,
		const std::reference_wrapper<const Topology>& topology,
		const std::chrono::high_resolution_clock::duration& timeout,
		const unsigned int& thread_count
	) : Application{
		header_space,
		state_space,
		topology,
		topology.get().get_database_name(),
		timeout,
		thread_count
	    },
	    states{},
	    mutex{} {}

	void Database::setup() {
		Application::setup();

		set_handler(
			get_header_space().get_state_header(),
			std::bind(
				&Database::handle_state,
				this,
				std::placeholders::_1
			)
		);

		get_thread_pool().add(std::bind(&Database::sync, this));
		std::this_thread::sleep_for(get_timeout());
	}

	const std::chrono::high_resolution_clock::duration
		Database::default_timeout{
		std::chrono::seconds(1)
	};

	const unsigned int Database::default_thread_count{4};

	const std::chrono::high_resolution_clock::duration&
		Database::get_default_timeout() {
		return default_timeout;
	}

	const unsigned int& Database::get_default_thread_count() {
		return default_thread_count;
	}

	const std::unordered_map<std::string, std::string>&
		Database::get_states() const {
		return states;
	}

	const std::mutex& Database::get_mutex() const {
		return mutex;
	}

	std::unordered_map<std::string, std::string>&
		Database::get_states() {
		return states;
	}

	std::mutex& Database::get_mutex() {
		return mutex;
	}

	std::vector<std::string> Database::get_data() {
		std::scoped_lock lock{get_mutex()};
		std::vector<std::string> data;

		get_logger() << Logger::Severity::information
			<< "Reading all "
			<< get_states().size()
			<< " key-value(s)..."
			<< std::endl;

		for (const auto& [key, value] : get_states()) {
			data.push_back(key);
			data.push_back(value);
		}

		return data;
	}
	
	void Database::set_data(
		const std::vector<std::string>& data
	) {
		std::scoped_lock lock{get_mutex()};

		if (data.size() % 2 == 1) {
			get_logger() << Logger::Severity::error
				<< "Unpaired elements in the data. "
				<< "This data will not be written."
				<< std::endl;

			return;
		}

		get_logger() << Logger::Severity::information
			<< "Writing "
			<< data.size() / 2
			<< " key-value(s)..."
			<< std::endl;

		for (std::size_t i{}; i + 1 < data.size(); i += 2)
			get_states().emplace(data[i], data[i + 1]);
	}

	std::vector<std::string>
		Database::handle_state(const Messenger::Message& message) {
		std::scoped_lock lock{get_mutex()};

		if (message.get_data().size() == 1) {
			auto key = message.get_data().front();

			get_logger() << Logger::Severity::error
				<< "Getting value for key: "
				<< key
				<< "..."
				<< std::endl;

			if (!get_states().count(key)) {
				get_logger() << Logger::Severity::information
					<< "The key: "
					<< key
					<< " does not exist."
					<< std::endl;

				return {};
			}

			auto value = get_states().at(key);

			get_logger() << Logger::Severity::error
				<< "Replying with corresponding value: "
				<< value
				<< "..."
				<< std::endl;

			return {value};
		} else if (message.get_data().size() == 2) {
			auto key = message.get_data().front();
			auto value = message.get_data().back();

			get_logger() << Logger::Severity::error
				<< "Setting key-value pair: "
				<< key
				<< ", "
				<< value
				<< "..."
				<< std::endl;

			get_states()[key] = value;

			for (const auto& peripheral_name
					: get_topology().get_peripheral_names())
				get_messenger().send(
					peripheral_name,
					get_header_space().get_state_header(),
					{key, value}
				);

			return {};
		}

		get_logger() << Logger::Severity::error
			<< "State expects 1 or 2 arguments, but "
			<< message.get_data().size()
			<< " argument(s) were supplied. "
			<< "This message will be ignored."
			<< std::endl;

		return {};
	}

	void Database::sync() {
		get_logger() << Logger::Severity::information
			<< "Syncing with "
			<< get_topology().get_replica_name()
			<< "..."
			<< std::endl;

		auto message = communicate(
			get_topology().get_replica_name(),
			get_header_space().get_data_header(),
			{},
			1
		);

		set_data(message.get_data());

		while (get_status()) {
			auto data = get_data();

			if (!data.empty())
				get_messenger().send(
					get_topology().get_replica_name(),
					get_header_space().get_data_header(),
					data
				);

			std::this_thread::sleep_for(get_timeout());
		}
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::State_space state_space;
	Revolution::Topology topology;
	Revolution::Database database{header_space, state_space, topology};

	database.main();

	return 0;
}
