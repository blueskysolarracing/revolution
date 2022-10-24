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
	class Messenger {
	public:
		struct Message {
			static Message deserialize(const std::string& raw_message);

			explicit Message(
				const std::string& sender_name,
				const std::string& header,
				const std::vector<std::string>& data = {}
			);

			std::string serialize() const;
			std::string to_string() const;

			const std::string sender_name;
			const std::string header;
			const std::vector<std::string> data;
		};

		struct Configuration {
			explicit Configuration(
				const std::string& name,
				const unsigned int& priority = 0,
				const int& oflags = O_RDWR | O_CREAT,
				const mode_t& mode = 0644,
				const bool& unlink = true
			);

			const std::string name;
			const unsigned int priority;
			const int oflags;
			const mode_t mode;
			const bool unlink;
		};

		explicit Messenger(
			const Configuration& configuration,
			Logger& logger
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
		const Configuration& get_configuration() const;
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

		const Configuration configuration;
		Logger& logger;
		std::unordered_map<std::string, mqd_t> descriptors;
	};
}

#endif	// REVOLUTION_MESSENGER_H
