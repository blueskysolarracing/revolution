#ifndef REVOLUTION_INSTANCE_H
#define REVOLUTION_INSTANCE_H

#include "application.h"
#include "topology.h"

namespace Revolution {
	class Instance : public Application {
	public:
		Instance(
			const std::string& name,
			const Logger::Configuration& logger_configuration,
			const Messenger::Configuration& messenger_configuration,
			const Topology& topology,
			const Header_space& header_space,
			const Key_space& key_space
		);
	protected:
		const Topology& get_topology() const;
		const Header_space& get_header_space() const;
		const Key_space& get_key_space() const;
		const std::unordered_map<std::string, std::string>& get_states() const;
		std::unordered_map<std::string, std::string>& get_states();
		std::vector<std::string> get_state_data() const;

		virtual void handle_get(const Messenger::Message& message);
		virtual void handle_set(const Messenger::Message& message);
		virtual void handle_reset(const Messenger::Message& message);
		virtual void handle_exit(const Messenger::Message& message);
	private:
		const Topology topology;
		const Header_space header_space;
		const Key_space key_space;
		std::unordered_map<std::string, std::string> states;
	};
}

#endif	// REVOLUTION_INSTANCE_H
