#include "peripheral.h"

#include <functional>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>

#include "application.h"
#include "configuration.h"
#include "messenger.h"
#include "logger.h"

namespace Revolution {
	Peripheral::Peripheral(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const State_space>& state_space,
		const std::reference_wrapper<const Topology>& topology,
		const std::string& name
	) : Application{header_space, state_space, topology, name} {}

	std::optional<std::string>
		Peripheral::get_state(const std::string& key) {
		auto message = communicate(
			get_topology().get_database(),
			get_header_space().get_state(),
			{key}
		);

		if (message.get_data().size() != 1) {
			if (!message.get_data().empty())
				get_logger() << Logger::Severity::error
					<< "Unexpected elements in the reply."
					<< std::endl;

			return std::nullopt;
		}

		return message.get_data().front();
	}

	void Peripheral::set_state(
		const std::string& key,
		const std::string& value
	) {
		communicate(
			get_topology().get_database(),
			get_header_space().get_state(),
			{key, value}
		);
	}

	bool Peripheral::get_gpio(
		const std::string& device,
		const unsigned int& offset
	) {
		auto message = communicate(
			get_topology().get_controller(),
			get_header_space().get_gpio(),
			{device, std::to_string(offset)}
		);

		if (message.get_data().size() != 1) {
			get_logger() << Logger::Severity::error
				<< "Invalid number of elements in the reply."
				<< std::endl;

			return false;
		}

		auto raw_active_low = message.get_data().front();

		return (bool) std::stoi(raw_active_low);
	}

	void Peripheral::set_gpio(
		const std::string& device,
		const unsigned int& offset,
		const bool& active_low
	) {
		communicate(
			get_topology().get_controller(),
			get_header_space().get_gpio(),
			{
				device,
				std::to_string(offset),
				std::to_string((int) active_low)
			}
		);
	}

	std::string Peripheral::receive_spi(const std::string& device) {
		auto message = communicate(
			get_topology().get_controller(),
			get_header_space().get_spi(),
			{device}
		);

		if (message.get_data().size() != 1) {
			get_logger() << Logger::Severity::error
				<< "Invalid number of elements in the reply."
				<< std::endl;

			return "";
		}

		return message.get_data().front();
	}

	void Peripheral::send_spi(
		const std::string& device,
		const std::string& tx
	) {
		communicate(
			get_topology().get_controller(),
			get_header_space().get_spi(),
			{device, tx}
		);
	}

	void Peripheral::set_gpio_watcher(
		const std::string& device,
		const unsigned int& offset,
		const Gpio_watcher& gpio_watcher
	) {
		std::scoped_lock lock{get_gpio_watcher_mutex()};

		get_gpio_watchers()[device][offset] = gpio_watcher;
	}

	void Peripheral::set_state_watcher(
		const std::string& key,
		const State_watcher& state_watcher
	) {
		std::scoped_lock lock{get_state_watcher_mutex()};

		get_state_watchers()[key] = state_watcher;
	}

	void Peripheral::setup() {
		Application::setup();

		set_handler(
			get_header_space().get_gpio(),
			std::bind(
				&Peripheral::handle_gpio,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_state(),
			std::bind(
				&Peripheral::handle_state,
				this,
				std::placeholders::_1
			)
		);
	}

	const std::unordered_map<
		std::string,
		std::unordered_map<unsigned int, Peripheral::Gpio_watcher>
	>& Peripheral::get_gpio_watchers() const {
		return gpio_watchers;
	}

	const std::mutex& Peripheral::get_gpio_watcher_mutex() const {
		return gpio_watcher_mutex;
	}

	const std::unordered_map<std::string, Peripheral::State_watcher>&
		Peripheral::get_state_watchers() const {
		return state_watchers;
	}

	const std::mutex& Peripheral::get_state_watcher_mutex() const {
		return state_watcher_mutex;
	}

	std::unordered_map<
		std::string,
		std::unordered_map<unsigned int, Peripheral::Gpio_watcher>
	>& Peripheral::get_gpio_watchers() {
		return gpio_watchers;
	}

	std::mutex& Peripheral::get_gpio_watcher_mutex() {
		return gpio_watcher_mutex;
	}

	std::unordered_map<std::string, Peripheral::State_watcher>&
		Peripheral::get_state_watchers() {
		return state_watchers;
	}

	std::mutex& Peripheral::get_state_watcher_mutex() {
		return state_watcher_mutex;
	}

	std::optional<
		const std::reference_wrapper<const Peripheral::Gpio_watcher>
	> Peripheral::get_gpio_watcher(
		const std::string& device,
		const unsigned int& offset
	) {
		std::scoped_lock lock{get_gpio_watcher_mutex()};

		if (!get_gpio_watchers().count(device)
				|| !get_gpio_watchers().at(device).count(offset))
			return std::nullopt;

		return get_gpio_watchers().at(device).at(offset);
	}

	std::optional<
		const std::reference_wrapper<const Peripheral::State_watcher>
	> Peripheral::get_state_watcher(const std::string& key) {
		std::scoped_lock lock{get_state_watcher_mutex()};

		if (!get_state_watchers().count(key))
			return std::nullopt;

		return get_state_watchers().at(key);
	}

	std::vector<std::string>
		Peripheral::handle_gpio(const Messenger::Message& message) {
		if (message.get_data().size() != 3) {
			get_logger() << Logger::Severity::error
				<< "Gpio expects 3 arguments, but "
				<< message.get_data().size()
				<< " argument(s) were supplied. "
				<< "The message will be ignored."
				<< std::endl;

			return {};
		}

		const auto& device = message.get_data().front();
		const auto& raw_offset = message.get_data()[1];
		const auto& raw_active_low = message.get_data().back();
		unsigned int offset = std::stoi(raw_offset);
		bool active_low = std::stoi(raw_active_low);
		const auto gpio_watcher = get_gpio_watcher(device, offset);

		if (gpio_watcher)
			gpio_watcher.value()(device, offset, active_low);

		return {};
	}

	std::vector<std::string>
		Peripheral::handle_state(const Messenger::Message& message) {
		if (message.get_data().size() != 2) {
			get_logger() << Logger::Severity::error
				<< "State expects 2 arguments, but "
				<< message.get_data().size()
				<< " argument(s) were supplied. "
				<< "The message will be ignored."
				<< std::endl;

			return {};
		}

		const auto& key = message.get_data().front();
		const auto& value = message.get_data().back();
		const auto state_watcher = get_state_watcher(key);

		if (state_watcher)
			state_watcher.value()(key, value);

		return {};
	}
}
