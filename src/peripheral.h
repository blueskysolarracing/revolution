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
			const std::string& name,
			const std::chrono::high_resolution_clock::duration&
				timeout,
			const unsigned int& thread_count
		);
	protected:
		using Watcher = std::function<
			void(const std::string&, const std::string&)
		>;

		std::optional<std::string> get_state(const std::string& key);
		void set_state(
			const std::string& key,
			const std::string& value
		);
		void set_watcher(
			const std::string& key,
			const Watcher& watcher
		);

		virtual void setup() override;
	private:
		const std::unordered_map<std::string, Watcher>&
			get_watchers() const;
		const std::mutex& get_mutex() const;

		std::unordered_map<std::string, Watcher>& get_watchers();
		std::mutex& get_mutex();

		std::optional<const std::reference_wrapper<const Watcher>>
			get_watcher(const std::string& key);

		std::vector<std::string>
			handle_state(const Messenger::Message& message);

		std::unordered_map<std::string, Watcher> watchers;
		std::mutex mutex;
	};
}

#endif	// REVOLUTION_PERIPHERAL_H
