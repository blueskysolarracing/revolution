#ifndef REVOLUTION_MESSENGER_H
#define REVOLUTION_MESSENGER_H

#include <chrono>
#include <optional>
#include <string>
#include <system_error>
#include <vector>

namespace Revolution {
	class Messenger {
	public:
		using Timeout = std::chrono::high_resolution_clock::duration;

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
				const unsigned int& identity = get_count()++
 			);

			const std::string& get_sender_name() const;
			const std::string& get_recipient_name() const;
			const std::string& get_header() const;
			const std::vector<std::string>& get_data() const;
			const unsigned int& get_priority() const;
			const unsigned int& get_identity() const;

			std::string serialize() const;
		private:
			static unsigned int count;

			static unsigned int& get_count();

			const std::string sender_name;
			const std::string recipient_name;
			const std::string header;
			const std::vector<std::string> data;
			const unsigned int priority;
			const unsigned int identity;
		};

		class Error : public std::system_error {
		public:
			explicit Error(const std::string& message);
		};

		Message receive(const std::string& recipient_name) const;
		std::optional<Message> timed_receive(
			const std::string& recipient_name,
			const Timeout& timeout = get_default_timeout()
		) const;

		void send(const Message& message) const;
		bool timed_send(
			const Message& message,
			const Timeout& timeout = get_default_timeout()
		) const;
	private:
		static const Timeout default_timeout;

		static const Timeout& get_default_timeout();
	};
}

#endif	// REVOLUTION_MESSENGER_H
