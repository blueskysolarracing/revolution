#include "controller.h"

#include <functional>
#include <string>

namespace Revolution {
	// TODO: https://developer.toradex.com/linux-bsp/application-development/peripheral-access/gpio-linux
	Controller::Controller(const std::string& device) : device{device} {}

	const std::string& Controller::get_device() const {
		return device;
	}

	GPIO::GPIO(const std::string& device, const unsigned int& offset)
		: Controller{device}, offset{offset} {}

	const unsigned int& GPIO::get_offset() const {
		return offset;
	}

	bool GPIO::get_active_low() const {
		// TODO: https://github.com/toradex/torizon-samples/blob/bullseye/gpio/c/gpio-toggle.c

		return false;
	}

	void GPIO::set_active_low(const bool& active_low) const {
		// TODO: https://github.com/toradex/torizon-samples/blob/bullseye/gpio/c/gpio-toggle.c

		(void) active_low;
	}

	void GPIO::monitor(
		const std::function<
			void(
				const std::string&,
				const unsigned int&,
				const bool&
			)
		>& handler
	) const {
		// TODO: https://github.com/toradex/torizon-samples/blob/bullseye/gpio/c/gpio-event.c

		(void) handler;
	}

	const std::string PWM::Polarity::normal{"normal"};
	const std::string PWM::Polarity::inversed{"inversed"};

	void PWM::enable(
		const unsigned int& period,
		const unsigned int& duty_cycle,
		const Polarity& polarity
	) const {
		// TODO: https://github.com/toradex/torizon-samples/tree/bullseye/pwm

		(void) period;
		(void) duty_cycle;
		(void) polarity;
	}

	void PWM::disable() const {
		// TODO: https://github.com/toradex/torizon-samples/tree/bullseye/pwm
	}

	void SPI::transmit(const std::string& data) const {
		// TODO: https://github.com/torvalds/linux/blob/v5.15/tools/spi/spidev_test.c

		(void) data;
	}

	std::string SPI::receive() const {
		// TODO: https://github.com/torvalds/linux/blob/v5.15/tools/spi/spidev_test.c

		return "";
	}

	std::string SPI::transmit_and_receive(const std::string& data) const {
		// TODO: https://github.com/torvalds/linux/blob/v5.15/tools/spi/spidev_test.c

		(void) data;

		return "";
	}

	void UART::transmit(const std::string& data) const {
		// TODO: https://developer.toradex.com/linux-bsp/application-development/peripheral-access/uart-linux#boards

		(void) data;
	}

	std::string UART::receive() const {
		// TODO: https://developer.toradex.com/linux-bsp/application-development/peripheral-access/uart-linux#boards

		return "";
	}
}
