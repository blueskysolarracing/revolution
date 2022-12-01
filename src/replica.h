#ifndef REVOLUTION_REPLICA_H
#define REVOLUTION_REPLICA_H

#include <functional>
#include <mutex>
#include <string>
#include <vector>

#include "application.h"
#include "configuration.h"
#include "messenger.h"

namespace Revolution {
	class Replica : public Application {
	public:
		explicit Replica(
			const std::reference_wrapper<const Header_space>&
				header_space,
			const std::reference_wrapper<const Key_space>&
				key_space,
			const std::reference_wrapper<const Topology>& topology
		);
	protected:
		void setup() override;
	private:
		const std::vector<std::string>& get_state_data() const;
		const std::mutex& get_state_data_mutex() const;

		std::vector<std::string>& get_state_data();
		std::mutex& get_state_data_mutex();

		std::vector<std::string>
			handle_get(const Messenger::Message& message);
		std::vector<std::string>
			handle_set(const Messenger::Message& message);

		std::vector<std::string> state_data;
		std::mutex state_data_mutex;
	};
}

#endif	// REVOLUTION_REPLICA_H
