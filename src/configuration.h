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
			const std::string& exit = "EXIT",
			const std::string& get = "GET",
			const std::string& gpio = "GPIO",
			const std::string& key = "KEY",
			const std::string& pwm = "PWM",
			const std::string& response = "RESPONSE",
			const std::string& set = "SET",
			const std::string& spi = "SPI",
			const std::string& status = "STATUS",
			const std::string& uart = "UART"
		);

		const std::string& get_abort() const;
		const std::string& get_exit() const;
		const std::string& get_get() const;
		const std::string& get_gpio() const;
		const std::string& get_key() const;
		const std::string& get_pwm() const;
		const std::string& get_response() const;
		const std::string& get_set() const;
		const std::string& get_spi() const;
		const std::string& get_status() const;
		const std::string& get_uart() const;
	private:
		const std::string abort;
		const std::string exit;
		const std::string get;
		const std::string gpio;
		const std::string key;
		const std::string pwm;
		const std::string response;
		const std::string set;
		const std::string spi;
		const std::string status;
		const std::string uart;
	};

	class Key_space {};

	class Topology {
	public:
		explicit Topology(
			const std::string& database = "database",
			const std::string& replica = "replica",
			const std::string& hardware = "hardware",
			const std::string& display = "display"
		);

		const std::string& get_database() const;
		const std::string& get_replica() const;
		const std::string& get_hardware() const;
		const std::string& get_display() const;

		const std::vector<std::reference_wrapper<const std::string>>
			get_peripherals() const;
	private:
		const std::string database;
		const std::string replica;
		const std::string hardware;
		const std::string display;
	};
}

#endif  // REVOLUTION_CONFIGURATION_H
