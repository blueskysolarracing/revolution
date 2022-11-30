#ifndef REVOLUTION_APPLICATION_H
#define REVOLUTION_APPLICATION_H

#include <atomic>
#include <condition_variable>
#include <functional>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

#include "configuration.h"
#include "heart.h"
#include "logger.h"
#include "messenger.h"
#include "worker_pool.h"

namespace Revolution {
	class Application {
	public:
		explicit Application(
			const std::reference_wrapper<const Header_space>&
				header_space,
			const std::reference_wrapper<const Key_space>&
				key_space,
			const std::reference_wrapper<const Topology>& topology
		);

		void main();
	protected:
		using Handler = std::function<
			std::vector<std::string>(const Messenger::Message&)
		>;

		const Header_space& get_header_space() const;
		const Key_space& get_key_space() const;
		const Topology& get_topology() const;
		const Logger& get_logger() const;
		const Worker_pool& get_worker_pool() const;
		const std::atomic_bool& get_status() const;

		Worker_pool& get_worker_pool();
		std::atomic_bool& get_status();

		void set_handler(
			const std::string& header,
			const Handler& handler
		);
		std::optional<std::string> get_state(const std::string& key);
		void set_state(
			const std::string& key,
			const std::string& value
		);
		virtual const std::string& get_name() const = 0;

		Messenger::Message send(
			const std::string& recipient_name,
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		) const;
		Messenger::Message communicate(
			const std::string& recipient_name,
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		);

		virtual void setup();
	private:
		const Messenger& get_messenger() const;
		const Heart& get_heart() const;
		const std::unordered_map<std::string, Handler>&
			get_handlers() const;
		const std::mutex& get_handler_mutex() const;
		const std::unordered_map<
			unsigned int,
			std::optional<Messenger::Message>
		>& get_responses() const;
		const std::mutex& get_response_mutex() const;
		const std::condition_variable&
			get_response_condition_variable() const;

		Heart& get_heart();
		std::unordered_map<std::string, Handler>& get_handlers();
		std::mutex& get_handler_mutex();
		std::unordered_map<
			unsigned int,
			std::optional<Messenger::Message>
		>& get_responses();
		std::mutex& get_response_mutex();
		std::condition_variable& get_response_condition_variable();

		std::optional<const std::reference_wrapper<const Handler>>
			get_handler(const std::string& header);
		Messenger::Message
			get_response(const Messenger::Message& message);
		void set_response(const Messenger::Message& message);

		std::vector<std::string>
			handle_abort(const Messenger::Message& message);
		std::vector<std::string>
			handle_exit(const Messenger::Message& message);
		std::vector<std::string>
			handle_response(const Messenger::Message& message);
		std::vector<std::string>
			handle_status(const Messenger::Message& message) const;

		void handle(const Messenger::Message& message);
		void help_handle(const Messenger::Message& message);
		void run();

		const std::reference_wrapper<const Header_space> header_space;
		const std::reference_wrapper<const Key_space> key_space;
		const std::reference_wrapper<const Topology> topology;
		const Logger logger;
		const Messenger messenger;
		Heart heart;
		Worker_pool worker_pool;
		std::atomic_bool status;
		std::unordered_map<std::string, Handler> handlers;
		std::mutex handler_mutex;
		std::unordered_map<
			unsigned int,
			std::optional<Messenger::Message>
		> responses;
		std::mutex response_mutex;
		std::condition_variable response_condition_variable;
	};
}

#endif	// REVOLUTION_APPLICATION_H
