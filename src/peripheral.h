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
			const std::reference_wrapper<const State_space>&
				state_space,
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
		using State_watcher = std::function<
			void(const std::string&, const std::string&)
		>;

		std::optional<std::string> get_state(const std::string& key);
		void set_state(
			const std::string& key,
			const std::string& value
		);
		bool get_gpio(
			const std::string& device,
			const unsigned int& offset
		);
		void set_gpio(
			const std::string& device,
			const unsigned int& offset,
			const bool& active_low
		);
		std::string receive_spi(const std::string& device);
		void send_spi(
			const std::string& device,
			const std::string& tx
		);

		void set_gpio_watcher(
			const std::string& device,
			const unsigned int& offset,
			const Gpio_watcher& gpio_watcher
		);
		void set_state_watcher(
			const std::string& key,
			const State_watcher& state_watcher
		);

		virtual void setup() override;
	private:
		const std::unordered_map<
			std::string,
			std::unordered_map<unsigned int, Gpio_watcher>
		>& get_gpio_watchers() const;
		const std::mutex& get_gpio_watcher_mutex() const;
		const std::unordered_map<std::string, State_watcher>&
			get_state_watchers() const;
		const std::mutex& get_state_watcher_mutex() const;

		std::unordered_map<
			std::string,
			std::unordered_map<unsigned int, Gpio_watcher>
		>& get_gpio_watchers();
		std::mutex& get_gpio_watcher_mutex();
		std::unordered_map<std::string, State_watcher>&
			get_state_watchers();
		std::mutex& get_state_watcher_mutex();

		std::optional<const std::reference_wrapper<const Gpio_watcher>>
			get_gpio_watcher(
			const std::string& device,
			const unsigned int& gpio
		);
		std::optional<const std::reference_wrapper<const State_watcher>>
			get_state_watcher(const std::string& key);

		std::vector<std::string>
			handle_gpio(const Messenger::Message& message);
		std::vector<std::string>
			handle_state(const Messenger::Message& message);

		std::unordered_map<
			std::string,
			std::unordered_map<unsigned int, Gpio_watcher>
		> gpio_watchers;
		std::mutex gpio_watcher_mutex;
		std::unordered_map<std::string, State_watcher> state_watchers;
		std::mutex state_watcher_mutex;
	};
}

#endif	// REVOLUTION_PERIPHERAL_H
