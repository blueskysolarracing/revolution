#ifndef REVOLUTION_CONFIGURATION_H
#define REVOLUTION_CONFIGURATION_H

#include <functional>
#include <string>
#include <vector>

namespace Revolution {
	class Header_space {
	public:
		explicit Header_space(
			const std::string& abort = "ABORT",
			const std::string& data = "DATA",
			const std::string& exit = "EXIT",
			const std::string& response = "RESPONSE",
			const std::string& state = "STATE",
			const std::string& status = "STATUS"
		);

		const std::string& get_abort() const;
		const std::string& get_data() const;
		const std::string& get_exit() const;
		const std::string& get_response() const;
		const std::string& get_state() const;
		const std::string& get_status() const;
	private:
		const std::string abort;
		const std::string data;
		const std::string exit;
		const std::string response;
		const std::string state;
		const std::string status;
	};

	class State_space {};

	class Topology {
	public:
		explicit Topology(
			const std::string& database = "database",
			const std::string& replica = "replica",
			const std::string& display = "display"
		);

		const std::string& get_database() const;
		const std::string& get_replica() const;
		const std::string& get_display() const;

		const std::vector<std::reference_wrapper<const std::string>>
			get_peripherals() const;
	private:
		const std::string database;
		const std::string replica;
		const std::string display;
	};
}

#endif  // REVOLUTION_CONFIGURATION_H
