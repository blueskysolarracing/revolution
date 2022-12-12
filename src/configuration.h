#ifndef REVOLUTION_CONFIGURATION_H
#define REVOLUTION_CONFIGURATION_H

#include <functional>
#include <string>
#include <vector>

namespace Revolution {
	class Header_space {
	public:
		explicit Header_space(
			const std::string& abort_header = "ABORT",
			const std::string& data_header = "DATA",
			const std::string& exit_header = "EXIT",
			const std::string& response_header = "RESPONSE",
			const std::string& state_header = "STATE",
			const std::string& status_header = "STATUS"
		);

		const std::string& get_abort_header() const;
		const std::string& get_data_header() const;
		const std::string& get_exit_header() const;
		const std::string& get_response_header() const;
		const std::string& get_state_header() const;
		const std::string& get_status_header() const;
	private:
		const std::string abort_header;
		const std::string data_header;
		const std::string exit_header;
		const std::string response_header;
		const std::string state_header;
		const std::string status_header;
	};

	class State_space {};

	class Topology {
	public:
		explicit Topology(
			const std::string& database_name = "database",
			const std::string& replica_name = "replica",
			const std::string& display_name = "display"
		);

		const std::string& get_database_name() const;
		const std::string& get_replica_name() const;
		const std::string& get_display_name() const;

		const std::vector<std::reference_wrapper<const std::string>>
			get_peripheral_names() const;
	private:
		const std::string database_name;
		const std::string replica_name;
		const std::string display_name;
	};
}

#endif  // REVOLUTION_CONFIGURATION_H
