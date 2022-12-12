#ifndef REVOLUTION_MESSENGER_H
#define REVOLUTION_MESSENGER_H

#include <atomic>
#include <chrono>
#include <functional>
#include <optional>
#include <string>
#include <system_error>
#include <vector>

namespace Revolution {
	class Messenger {
	public:
		class Message {
		public:
			static Message deserialize(
				const std::string& raw_message
			);

			explicit Message(
				const std::string& sender_name,
				const std::string& recipient_name,
				const std::string& header,
				const std::vector<std::string>& data = {},
				const unsigned int& priority = 0,
				const unsigned int& identifier = get_count()++
 			);

			bool operator==(const Message& that) const;

			const std::string& get_sender_name() const;
			const std::string& get_recipient_name() const;
			const std::string& get_header() const;
			const std::vector<std::string>& get_data() const;
			const unsigned int& get_priority() const;
			const unsigned int& get_identifier() const;

			std::string serialize() const;
			std::string to_string() const;
		private:
			static unsigned int count;

			static unsigned int& get_count();

			const std::string sender_name;
			const std::string recipient_name;
			const std::string header;
			const std::vector<std::string> data;
			const unsigned int priority;
			const unsigned int identifier;
		};

		class Error : public std::system_error {
		public:
			explicit Error(const std::string& message);
		};

		static void unlink(const std::string& name);

		Messenger(const std::string& sender_name);
		~Messenger();

		const std::string& get_sender_name() const;

		Message receive() const;
		std::optional<Message> timed_receive(
			const std::chrono::high_resolution_clock::duration&
				timeout
		) const;

		Message send(
			const std::string& recipient_name,
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		) const;
		std::optional<Message> timed_send(
			const std::chrono::high_resolution_clock::duration&
				timeout,
			const std::string& recipient_name,
			const std::string& header,
			const std::vector<std::string>& data = {},
			const unsigned int& priority = 0
		) const;

		void watch(
			const std::chrono::high_resolution_clock::duration&
				timeout,
			const std::atomic_bool& status,
			const std::function<void(const Message&)>& watcher
		) const;
	private:
		std::string sender_name;
	};
}

#endif	// REVOLUTION_MESSENGER_H
