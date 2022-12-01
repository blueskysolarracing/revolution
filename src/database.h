#ifndef REVOLUTION_DATABASE_H
#define REVOLUTION_DATABASE_H

#include <atomic>
#include <functional>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

#include "application.h"
#include "configuration.h"
#include "messenger.h"

namespace Revolution {
	class Database : public Application {
	public:
		using Timeout = std::chrono::high_resolution_clock::duration;

		explicit Database(
			const std::reference_wrapper<const Header_space>&
				header_space,
			const std::reference_wrapper<const Key_space>&
				key_space,
			const std::reference_wrapper<const Topology>& topology,
			const Timeout& timeout = get_default_timeout()
		);
	protected:
		void setup() override;
	private:
		static const Timeout default_timeout;

		static const Timeout& get_default_timeout();

		const Timeout& get_timeout() const;
		const std::unordered_map<std::string, std::string>&
			get_states() const;
		const std::mutex& get_state_mutex() const;

		std::unordered_map<std::string, std::string>& get_states();
		std::mutex& get_state_mutex();

		std::vector<std::string> get_state_data();
		void set_state_data(const std::vector<std::string>& state_data);

		std::optional<std::string> help_get_state(const std::string& key);
		void help_set_state(
			const std::string& key,
			const std::string& value
		);

		std::vector<std::string>
			handle_get(const Messenger::Message& message);
		std::vector<std::string>
			handle_set(const Messenger::Message& message);

		void sync();

		const Timeout timeout;
		std::unordered_map<std::string, std::string> states;
		std::mutex state_mutex;
	};
}

#endif	// REVOLUTION_DATABASE_H

