#ifndef REVOLUTION_PERIPHERAL_H
#define REVOLUTION_PERIPHERAL_H

#include <functional>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	class Peripheral : public Application {
	public:
		explicit Peripheral(
			const std::reference_wrapper<const Header_space>&
				header_space,
			const std::reference_wrapper<const Key_space>&
				key_space,
			const std::reference_wrapper<const Topology>& topology,
			const std::string& name
		);
	protected:
		using Gpio_watcher = std::function<
			void(
				const std::string&,
				const unsigned int&,
				const bool&
			)
		>;
		using Key_watcher = std::function<
			void(const std::string&, const std::string&)
		>;

		std::optional<std::string> get_state(const std::string& key);
		void set_state(
			const std::string& key,
			const std::string& value
		);

		void set_gpio_watcher(
			const std::string& bank,
			const unsigned int& gpio,
			const Gpio_watcher& gpio_watcher
		);
		void set_key_watcher(
			const std::string& key,
			const Key_watcher& key_watcher
		);

		virtual void setup() override;
	private:
		const std::unordered_map<
			std::string,
			std::unordered_map<unsigned int, Gpio_watcher>
		>& get_gpio_watchers() const;
		const std::mutex& get_gpio_watcher_mutex() const;
		const std::unordered_map<std::string, Key_watcher>&
			get_key_watchers() const;
		const std::mutex& get_key_watcher_mutex() const;

		std::unordered_map<
			std::string,
			std::unordered_map<unsigned int, Gpio_watcher>
		>& get_gpio_watchers();
		std::mutex& get_gpio_watcher_mutex();
		std::unordered_map<std::string, Key_watcher>& get_key_watchers();
		std::mutex& get_key_watcher_mutex();

		std::optional<const std::reference_wrapper<const Gpio_watcher>>
			get_gpio_watcher(
			const std::string& bank,
			const unsigned int& gpio
		);
		std::optional<const std::reference_wrapper<const Key_watcher>>
			get_key_watcher(const std::string& key);

		std::vector<std::string>
			handle_gpio(const Messenger::Message& message);
		std::vector<std::string>
			handle_key(const Messenger::Message& message);

		std::unordered_map<
			std::string,
			std::unordered_map<unsigned int, Gpio_watcher>
		> gpio_watchers;
		std::mutex gpio_watcher_mutex;
		std::unordered_map<std::string, Key_watcher> key_watchers;
		std::mutex key_watcher_mutex;
	};
}

#endif	// REVOLUTION_PERIPHERAL_H
