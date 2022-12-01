#include "peripheral.h"

#include <cassert>
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
		const std::reference_wrapper<const Key_space>& key_space,
		const std::reference_wrapper<const Topology>& topology,
		const std::string& name
	) : Application{header_space, key_space, topology, name} {}

	std::optional<std::string>
		Peripheral::get_state(const std::string& key) {
		auto message = communicate(
			get_topology().get_database(),
			get_header_space().get_get(),
			{key}
		);

		if (message.get_data().empty())
			return std::nullopt;

		assert(message.get_data().size() == 1);

		return message.get_data().front();
	}

	void Peripheral::set_state(
		const std::string& key,
		const std::string& value
	) {
		communicate(
			get_topology().get_database(),
			get_header_space().get_set(),
			{key, value}
		);
	}

	void Peripheral::set_gpio_watcher(
		const std::string& bank,
		const unsigned int& gpio,
		const Gpio_watcher& gpio_watcher
	) {
		std::scoped_lock lock{get_gpio_watcher_mutex()};

		get_gpio_watchers()[bank][gpio] = gpio_watcher;
	}

	void Peripheral::set_key_watcher(
		const std::string& key,
		const Key_watcher& key_watcher
	) {
		std::scoped_lock lock{get_key_watcher_mutex()};

		get_key_watchers()[key] = key_watcher;
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
			get_header_space().get_key(),
			std::bind(
				&Peripheral::handle_key,
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

	const std::unordered_map<std::string, Peripheral::Key_watcher>&
		Peripheral::get_key_watchers() const {
		return key_watchers;
	}

	const std::mutex& Peripheral::get_key_watcher_mutex() const {
		return key_watcher_mutex;
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

	std::unordered_map<std::string, Peripheral::Key_watcher>&
		Peripheral::get_key_watchers() {
		return key_watchers;
	}

	std::mutex& Peripheral::get_key_watcher_mutex() {
		return key_watcher_mutex;
	}

	std::optional<
		const std::reference_wrapper<const Peripheral::Gpio_watcher>
	> Peripheral::get_gpio_watcher(
		const std::string& bank,
		const unsigned int& gpio
	) {
		std::scoped_lock lock{get_gpio_watcher_mutex()};

		if (!get_gpio_watchers().count(bank)
				|| !get_gpio_watchers().at(bank).count(gpio))
			return std::nullopt;

		return get_gpio_watchers().at(bank).at(gpio);
	}

	std::optional<
		const std::reference_wrapper<const Peripheral::Key_watcher>
	> Peripheral::get_key_watcher(const std::string& key) {
		std::scoped_lock lock{get_key_watcher_mutex()};

		if (!get_key_watchers().count(key))
			return std::nullopt;

		return get_key_watchers().at(key);
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

		const auto& bank = message.get_data().front();
		const auto& raw_gpio = message.get_data()[1];
		const auto& raw_status = message.get_data().back();
		unsigned int gpio = std::stoi(raw_gpio);
		bool status = std::stoi(raw_status);
		const auto gpio_watcher = get_gpio_watcher(bank, gpio);

		if (gpio_watcher)
			gpio_watcher.value()(bank, gpio, status);

		return {};
	}

	std::vector<std::string>
		Peripheral::handle_key(const Messenger::Message& message) {
		if (message.get_data().size() != 2) {
			get_logger() << Logger::Severity::error
				<< "Key expects 2 arguments, but "
				<< message.get_data().size()
				<< " argument(s) were supplied. "
				<< "The message will be ignored."
				<< std::endl;

			return {};
		}

		const auto& key = message.get_data().front();
		const auto& value = message.get_data().back();
		const auto key_watcher = get_key_watcher(key);

		if (key_watcher)
			key_watcher.value()(key, value);

		return {};
	}
}
