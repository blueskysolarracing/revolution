#include "controller.h"

#include <functional>
#include <string>
#include <vector>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	Controller::Controller(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const State_space>& state_space,
		const std::reference_wrapper<const Topology>& topology
	) : Application{
		header_space,
		state_space,
		topology,
		topology.get().get_controller()
	    } {}

	void Controller::setup() {
		Application::setup();

		set_handler(
			get_header_space().get_gpio(),
			std::bind(
				&Controller::handle_gpio,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_pwm(),
			std::bind(
				&Controller::handle_pwm,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_spi(),
			std::bind(
				&Controller::handle_spi,
				this,
				std::placeholders::_1
			)
		);
		set_handler(
			get_header_space().get_uart(),
			std::bind(
				&Controller::handle_uart,
				this,
				std::placeholders::_1
			)
		);

		// TODO: https://github.com/toradex/torizon-samples/blob/bullseye/gpio/c/gpio-event.c
		// TODO: https://developer.toradex.com/linux-bsp/application-development/peripheral-access/gpio-linux
	}

	std::vector<std::string>
		Controller::handle_gpio(const Messenger::Message& message) {
		// TODO: https://github.com/toradex/torizon-samples/blob/bullseye/gpio/c/gpio-toggle.c
		// TODO: https://developer.toradex.com/linux-bsp/application-development/peripheral-access/gpio-linux

		if (message.get_data().size() == 2) {
			// const auto& device = message.get_data().front();
			// const auto& raw_offset = message.get_data().back();
			// unsigned int offset = (unsigned int) std::stoi(raw_offset);
			
			// TODO
		} else if (message.get_data().size() == 3) {
			// const auto& device = message.get_data().front();
			// const auto& raw_offset = message.get_data()[1];
			// const auto& raw_active_low = message.get_data().back();
			// unsigned int offset = (unsigned int) std::stoi(raw_offset);
			// bool active_low = (bool) std::stoi(raw_active_low);

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
		Controller::handle_pwm(const Messenger::Message& message) {
		// TODO: https://github.com/toradex/torizon-samples/tree/bullseye/pwm

		if (message.get_data().size() == 1) {
			// const auto& device = message.get_data().front();
			
			// TODO
		} else if (message.get_data().size() == 2) {
			// const auto& device = message.get_data().front();

			// TODO
		}

		get_logger() << Logger::Severity::error
			<< "Pwm expects 1 or 2 arguments, but "
			<< message.get_data().size()
			<< " argument(s) were supplied. "
			<< "This message will be ignored."
			<< std::endl;

		return {};
	}

	std::vector<std::string>
		Controller::handle_spi(const Messenger::Message& message) {
		// TODO: https://github.com/torvalds/linux/blob/v5.15/tools/spi/spidev_test.c

		if (message.get_data().size() == 1) {
			// const auto& device = message.get_data().front();

			// TODO
		} else if (message.get_data().size() == 2) {
			// const auto& device = message.get_data().front();
			// const auto& tx = message.get_data().back();

			// TODO
		}

		get_logger() << Logger::Severity::error
			<< "Spi expects 1 or 2 arguments, but "
			<< message.get_data().size()
			<< " argument(s) were supplied. "
			<< "This message will be ignored."
			<< std::endl;

		return {};
	}

	std::vector<std::string>
		Controller::handle_uart(const Messenger::Message& message) {
		// TODO: https://developer.toradex.com/linux-bsp/application-development/peripheral-access/uart-linux#boards

		if (message.get_data().size() == 1) {
			// const auto& device = message.get_data().front();
			
			// TODO
		} else if (message.get_data().size() == 2) {
			// const auto& device = message.get_data().front();
			// const auto& tx = message.get_data().back();

			// TODO
		}

		get_logger() << Logger::Severity::error
			<< "Uart expects 1 or 2 arguments, but "
			<< message.get_data().size()
			<< " argument(s) were supplied. "
			<< "This message will be ignored."
			<< std::endl;

		return {};
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::State_space state_space;
	Revolution::Topology topology;
	Revolution::Controller controller{header_space, state_space, topology};

	controller.main();

	return 0;
}
