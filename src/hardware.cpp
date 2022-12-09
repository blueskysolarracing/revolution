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
		if (message.get_data().size() == 2) {
			const auto& device = message.get_data().front();
			const auto& raw_offset = message.get_data().back();
			unsigned int offset = (unsigned int) std::stoi(raw_offset);
			
			// TODO
		} else if (message.get_data().size() == 3) {
			const auto& device = message.get_data().front();
			const auto& raw_offset = message.get_data()[1];
			const auto& raw_active_low = message.get_data().back();
			unsigned int offset = (unsigned int) std::stoi(raw_offset);
			bool active_low = (bool) std::stoi(raw_active_low);

			// TODO
		}

		get_logger() << Logger::Severity::error
			<< "Gpio expects 2 or 3 arguments, but "
			<< message.get_data().size()
			<< " argument(s) were supplied. "
			<< "This message will be ignored."
			<< std::endl;

		return {};
	}

	std::vector<std::string>
		Hardware::handle_pwm(const Messenger::Message& message) {
		return {};  // TODO
	}

	std::vector<std::string>
		Hardware::handle_spi(const Messenger::Message& message) {
		if (message.get_data().size() == 1) {
			const auto& device = message.get_data().front();

			// TODO
		} else if (message.get_data().size() == 2) {
			const auto& device = message.get_data().front();
			const auto& tx = message.get_data().back();

			// TODO
		}

		get_logger() << Logger::Severity::error
			<< "Gpio expects 1 or 2 arguments, but "
			<< message.get_data().size()
			<< " argument(s) were supplied. "
			<< "This message will be ignored."
			<< std::endl;

		return {};
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
