#include "display.h"

#include <chrono>
#include <functional>

#include "configuration.h"
#include "peripheral.h"

namespace Revolution {
	Display::Display(
		const std::reference_wrapper<const Header_space>& header_space,
		const std::reference_wrapper<const State_space>& state_space,
		const std::reference_wrapper<const Topology>& topology,
		const std::chrono::high_resolution_clock::duration& timeout,
		const unsigned int& thread_count
	) : Peripheral{
		header_space,
		state_space,
		topology,
		topology.get().get_display_name(),
		timeout,
		thread_count
	    } {}

	const std::chrono::high_resolution_clock::duration
		Display::default_timeout{
		std::chrono::seconds(1)
	};

	const unsigned int Display::default_thread_count{4};

	const std::chrono::high_resolution_clock::duration&
		Display::get_default_timeout() {
		return default_timeout;
	}

	const unsigned int& Display::get_default_thread_count() {
		return default_thread_count;
	}
}

int main() {
	Revolution::Header_space header_space;
	Revolution::State_space state_space;
	Revolution::Topology topology;
	Revolution::Display display{header_space, state_space, topology};

	display.main();

	return 0;
}
