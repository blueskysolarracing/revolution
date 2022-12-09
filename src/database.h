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
			const std::reference_wrapper<const State_space>&
				state_space,
			const std::reference_wrapper<const Topology>& topology,
			const Timeout& sync_timeout = get_default_sync_timeout()
		);
	protected:
		void setup() override;
	private:
		static const Timeout default_sync_timeout;

		static const Timeout& get_default_sync_timeout();

		const Timeout& get_sync_timeout() const;
		const std::unordered_map<std::string, std::string>&
			get_states() const;
		const std::mutex& get_state_mutex() const;

		std::unordered_map<std::string, std::string>& get_states();
		std::mutex& get_state_mutex();

		std::vector<std::string> get_data();
		void set_data(const std::vector<std::string>& data);

		std::vector<std::string>
			handle_state(const Messenger::Message& message);

		void sync();

		const Timeout sync_timeout;
		std::unordered_map<std::string, std::string> states;
		std::mutex state_mutex;
	};
}

#endif	// REVOLUTION_DATABASE_H
