#include "hardware.h"

#include <functional>
#include <string>
#include <vector>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	Hardware::Hardware(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const Key_space>& key_space,
		const std::reference_wrapper<const Topology>& topology
	) : Application{
		header_space,
		key_space,
		topology,
		topology.get().get_hardware()
	    } {}

	void Hardware::setup() {
		Application::setup();

		set_handler(
			get_header_space().get_gpio(),
			std::bind(
				&Hardware::handle_gpio,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_pwm(),
			std::bind(
				&Hardware::handle_pwm,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_spi(),
			std::bind(
				&Hardware::handle_spi,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_uart(),
			std::bind(
				&Hardware::handle_uart,
				this,
				std::placeholders::_1
			)
		);

		// TODO
	}

	std::vector<std::string>
		Hardware::handle_gpio(const Messenger::Message& message) {
		if (message.get_data().size() != 3) {
			get_logger() << Logger::Severity::error
				<< "Gpio expects 3 arguments, but "
				<< message.get_data().size()
				<< " argument(s) were supplied. "
				<< "The message will be ignored."
				<< std::endl;

			return {};
		}

		const auto& bank = message.get_data().front();
		const auto& raw_gpio = message.get_data()[1];
		const auto& raw_status = message.get_data().back();
		unsigned int gpio = std::stoi(raw_gpio);
		bool status = std::stoi(raw_status);

		return {};  // TODO
	}

	std::vector<std::string>
		Hardware::handle_pwm(const Messenger::Message& message) {
		return {};  // TODO
	}

	std::vector<std::string>
		Hardware::handle_spi(const Messenger::Message& message) {
		return {};  // TODO
	}

	std::vector<std::string>
		Hardware::handle_uart(const Messenger::Message& message) {
		return {};  // TODO
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::Key_space key_space;
	Revolution::Topology topology;
	Revolution::Hardware hardware{header_space, key_space, topology};

	hardware.main();

	return 0;
}
