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
			static Message deserialize(
				const std::string& raw_message
			);

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
				const std::string& full_name_prefix = "/",
				const unsigned int& priority = 0,
				const int& oflags = O_RDWR | O_CREAT,
				const mode_t& mode = 0644
			);

			const std::string name;
			const std::string full_name_prefix;
			const unsigned int priority;
			const int oflags;
			const mode_t mode;
		};

		explicit Messenger(
			const Configuration& configuration,
			Logger& logger
		);

		Message receive() const;
		std::optional<Message> receive(
			const std::chrono::system_clock::duration& timeout
		) const;

		void send(
			const std::string& name,
			const std::string& header,
			const std::vector<std::string>& data = {}
		) const;
		bool send(
			const std::string& name,
			const std::string& header,
			const std::vector<std::string>& data,
			const std::chrono::system_clock::duration& timeout
		) const;
		bool send(
			const std::string& name,
			const std::string& header,
			const std::chrono::system_clock::duration& timeout
		) const;
	private:
		const Configuration& get_configuration() const;
		Logger& get_logger() const;

		mqd_t open_descriptor(const std::string& name) const;
		void close_descriptor(mqd_t& descriptor) const;

		std::optional<Message> receive(
			std::function<
				ssize_t(
					const mqd_t&,
					std::string&,
					unsigned int&
				)
			> receiver
		) const;

		bool send(
			const std::string& name,
			const std::string& header,
			const std::vector<std::string>& data,
			std::function<
				int(
					const mqd_t&,
					const std::string&,
					const unsigned int&
				)
			> sender
		) const;

		const Configuration configuration;
		Logger& logger;
	};
}

#endif	// REVOLUTION_MESSENGER_H
