#ifndef REVOLUTION_DISPLAY_H
#define REVOLUTION_DISPLAY_H

#include <chrono>
#include <functional>

#include "configuration.h"
#include "peripheral.h"

namespace Revolution {
	class Display : public Peripheral {
	public:
		explicit Display(
			const std::reference_wrapper<const Header_space>&
				header_space,
			const std::reference_wrapper<const State_space>&
				state_space,
			const std::reference_wrapper<const Topology>& topology,
			const std::chrono::high_resolution_clock::duration&
				timeout = get_default_timeout(),
			const unsigned int& thread_count
				= get_default_thread_count()
		);
	private:
		static const std::chrono::high_resolution_clock::duration
			default_timeout;
		static const unsigned int default_thread_count;

		static const std::chrono::high_resolution_clock::duration&
			get_default_timeout();
		static const unsigned int& get_default_thread_count();
	};
}

#endif	// REVOLUTION_DISPLAY_H
