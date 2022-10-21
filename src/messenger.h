#ifndef REVOLUTION_MESSENGER_H
#define REVOLUTION_MESSENGER_H

#include <chrono>
#include <functional>
#include <optional>
#include <string>
#include <vector>

#include <mqueue.h>

#include "logger.h"

namespace Revolution {
	class Message {
	public:
		static Message deserialize(const std::string &raw_message);

		explicit Message(
			const std::string &sender_name,
			const std::string &header_name,
			const std::vector<std::string> &data = {}
		);

		const std::string &get_sender_name() const;
		const std::string &get_header_name() const;
		const std::vector<std::string> &get_data() const;

		std::string serialize() const;
	private:
		const std::string sender_name;
		const std::string header_name;
		const std::vector<std::string> data;
	};

	class Messenger {
	public:
		explicit Messenger(
			const std::string &name,
			const unsigned int &priority,
			Logger &logger
		);
		~Messenger();

		const std::string &get_name() const;
		const unsigned int &get_priority() const;

		Message receive();
		std::optional<Message> receive(
			const std::chrono::system_clock::time_point &timeout
		);

		void send(
			const std::string &recipient_name,
			const std::string &header_name,
			const std::vector<std::string> &data = {}
		);
		bool send(
			const std::chrono::system_clock::time_point &timeout,
			const std::string &recipient_name,
			const std::string &header_name,
			const std::vector<std::string> &data = {}
		);
	private:
		static const std::string name_prefix;
		static const int oflags;
		static const mode_t mode;

		static const std::string &get_name_prefix();
		static const int &get_oflags();
		static const mode_t &get_mode();

		static std::string get_full_name(const std::string &name);

		Logger &get_logger();
		std::unordered_map<std::string, mqd_t> &get_descriptors();

		std::string get_full_name();
		mqd_t &get_descriptor(const std::string &name);

		std::optional<Message> receive(
			std::function<ssize_t(mqd_t &, std::string &, unsigned int &)> receiver
		);

		bool send(
			const std::string &recipient_name,
			const std::string &header_name,
			const std::vector<std::string> &data,
			std::function<int(mqd_t &, const std::string &, const unsigned int &)> sender
		);

		const std::string name;
		const unsigned int priority;
		Logger &logger;
		std::unordered_map<std::string, mqd_t> descriptors;
	};
}

#endif	// REVOLUTION_MESSENGER_H
