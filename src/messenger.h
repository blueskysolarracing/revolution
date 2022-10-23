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
		static Message deserialize(const std::string& raw_message);

		explicit Message(
			const std::string& sender_name,
			const std::string& header,
			const std::vector<std::string>& data = {}
		);

		const std::string& get_sender_name() const;
		const std::string& get_header() const;
		const std::vector<std::string>& get_data() const;

		std::string serialize() const;
	private:
		const std::string sender_name;
		const std::string header;
		const std::vector<std::string> data;
	};

	class Messenger {
	public:
		explicit Messenger(
			Logger& logger,
			const std::string& name,
			const int& oflags = O_RDWR | O_CREAT,
			const mode_t& mode = 0644,
			const unsigned int& priority = 0,
			const bool& unlink_status = true
		);
		~Messenger();

		Message receive();
		std::optional<Message> receive(
			const std::chrono::system_clock::time_point& timeout
		);

		void send(
			const std::string& name,
			const std::string& header,
			const std::vector<std::string>& data = {}
		);
		bool send(
			const std::chrono::system_clock::time_point& timeout,
			const std::string& name,
			const std::string& header,
			const std::vector<std::string>& data = {}
		);
	private:
		const std::string& get_name() const;
		const int& get_oflags() const;
		const mode_t& get_mode() const;
		const unsigned int& get_priority() const;
		const bool& get_unlink_status() const;
		Logger& get_logger();
		std::unordered_map<std::string, mqd_t>& get_descriptors();

		mqd_t& get_descriptor(const std::string& name);

		std::optional<Message> receive(
			std::function<ssize_t(mqd_t&, std::string&, unsigned int&)> receiver
		);

		bool send(
			const std::string& name,
			const std::string& header,
			const std::vector<std::string>& data,
			std::function<int(mqd_t&, const std::string&, const unsigned int&)> sender
		);

		Logger& logger;
		const std::string name;
		const int oflags;
		const mode_t mode;
		const unsigned int priority;
		const bool unlink_status;
		std::unordered_map<std::string, mqd_t> descriptors;
	};
}

#endif	// REVOLUTION_MESSENGER_H
