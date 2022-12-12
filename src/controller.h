#ifndef REVOLUTION_CONTROLLER_H
#define REVOLUTION_CONTROLLER_H

#include <functional>
#include <string>

namespace Revolution {
	class Controller {
	public:
		explicit Controller(const std::string& device);

		const std::string& get_device() const;
	private:
		const std::string device;
	};

	class GPIO : public Controller {
	public:
		explicit GPIO(
			const std::string& device,
			const unsigned int& offset
		);

		const unsigned int& get_offset() const;

		bool get_active_low() const;
		void set_active_low(const bool& active_low) const;
		void monitor(
			const std::function<
				void(
					const std::string&,
					const unsigned int&,
					const bool&
				)
			>& handler
		) const;
	private:
		const unsigned int offset;
	};

	class PWM : public Controller {
	public:
		using Controller::Controller;

		class Polarity {
		public:
			static const std::string normal;
			static const std::string inversed;
		};

		void enable(
			const unsigned int& period,
			const unsigned int& duty_cycle,
			const Polarity& polarity
		) const;
		void disable() const;
	};

	class SPI : public Controller {
	public:
		using Controller::Controller;

		void transmit(const std::string& data) const;
		std::string receive() const;
		std::string transmit_and_receive(const std::string& data) const;
	};

	class UART : public Controller {
	public:
		using Controller::Controller;

		void transmit(const std::string& data) const;
		std::string receive() const;
	};
}

#endif	// REVOLUTION_CONTROLLER_H
