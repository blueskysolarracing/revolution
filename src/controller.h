#ifndef REVOLUTION_CONTROLLER_H
#define REVOLUTION_CONTROLLER_H

#include <functional>
#include <string>
#include <vector>

#include "application.h"
#include "configuration.h"

namespace Revolution {
	class Controller : public Application {
	public:
		explicit Controller(
			const std::reference_wrapper<const Header_space>&
				header_space,
			const std::reference_wrapper<const Key_space>&
				key_space,
			const std::reference_wrapper<const Topology>& topology
		);
	protected:
		void setup() override;
	private:
		std::vector<std::string>
			handle_gpio(const Messenger::Message& message);
		std::vector<std::string>
			handle_pwm(const Messenger::Message& message);
		std::vector<std::string>
			handle_spi(const Messenger::Message& message);
		std::vector<std::string>
			handle_uart(const Messenger::Message& message);
	};
}

#endif	// REVOLUTION_CONTROLLER_H
