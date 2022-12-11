#include "messenger.h"

#include <cerrno>
#include <chrono>
#include <cstddef>
#include <cstring>
#include <ctime>
#include <functional>
#include <optional>
#include <sstream>
#include <string>
#include <system_error>
#include <vector>

#include <fcntl.h>
#include <mqueue.h>
#include <sys/stat.h>

namespace Revolution {
	static mqd_t open_message_queue_descriptor(const std::string& name) {
		auto descriptor = mq_open(
			('/' + name).data(),
			O_RDWR | O_CREAT,
			0666,
			NULL
		);

		if (descriptor == (mqd_t) - 1)
			throw Messenger::Error{"Cannot open message queue"};

		return descriptor;
	}

	static void close_message_queue_descriptor(const mqd_t& descriptor) {
		auto status = mq_close(descriptor);

		if (status == -1)
			throw Messenger::Error{"Cannot close message queue"};
	}

	static mq_attr get_message_queue_attributes(const std::string& name) {
		mq_attr attributes;
		auto descriptor = open_message_queue_descriptor(name);
		auto status = mq_getattr(descriptor, &attributes);
		close_message_queue_descriptor(descriptor);

		if (status == -1)
			throw Messenger::Error{
				"Cannot get message queue attributes"
			};

		return attributes;
	}

	static std::optional<Messenger::Message> receive_from_message_queue(
		const std::string& recipient_name,
		const std::function<
			ssize_t(const mqd_t&, std::string&, unsigned int&)
		>& receiver
	) {
		auto attributes = get_message_queue_attributes(recipient_name);
		std::string raw_message(attributes.mq_msgsize, '\0');
		unsigned int priority;

		auto descriptor = open_message_queue_descriptor(recipient_name);
		auto received_size
			= receiver(descriptor, raw_message, priority);
		close_message_queue_descriptor(descriptor);

		if (received_size == -1) {
			if (errno == ETIMEDOUT)
				return std::nullopt;

			throw Messenger::Error{
				"Cannot receive from message queue"
			};
		}

		raw_message.resize(received_size);

		return Messenger::Message::deserialize(raw_message);
	}

	static bool send_to_message_queue(
		const Messenger::Message& message,
		const std::function<
			int(
				const mqd_t&,
				const std::string&,
				const unsigned int&
			)
		>& sender
	) {
		std::string raw_message{message.serialize()};
		unsigned int priority{message.get_priority()};

		auto descriptor = open_message_queue_descriptor(
			message.get_recipient_name()
		);
		auto status = sender(descriptor, raw_message, priority);
		close_message_queue_descriptor(descriptor);

		if (status == -1 && errno != ETIMEDOUT)
			throw Messenger::Error{"Cannot send to message queue"};

		return !status;
	}

	static void unlink_message_queue(const std::string& name) {
		auto status = mq_unlink(('/' + name).data());

		if (status == -1)
			throw Messenger::Error{"Cannot unlink message queue"};
	}

	static timespec convert_to_timespec(
		const std::chrono::high_resolution_clock::duration& duration
	) {
		auto seconds = std::chrono::duration_cast<std::chrono::seconds>(
			duration
		);
		auto nanoseconds
			= std::chrono::duration_cast<std::chrono::nanoseconds>(
				duration - seconds
			);

		return {seconds.count(), nanoseconds.count()};
	}

	Messenger::Message Messenger::Message::deserialize(
		const std::string& raw_message
	) {
		std::vector<std::string> tokens;
		std::size_t begin_index = 0, end_index = raw_message.find(',');

		while (end_index != std::string::npos) {
			tokens.push_back(
				raw_message.substr(
					begin_index,
					end_index - begin_index
				)
			);
			begin_index = end_index + 1;
			end_index = raw_message.find('\0', begin_index);
		}

		std::string sender_name = tokens[0];
		std::string recipient_name = tokens[1];
		std::string header = tokens[2];
		std::vector<std::string> data{
			std::next(tokens.begin(), 3),
			std::next(tokens.begin(), tokens.size() - 2)
		};
		unsigned int priority = std::stoul(tokens[tokens.size() - 2]);
		unsigned int identifier = std::stoul(tokens[tokens.size() - 1]);

		return Message{
			sender_name,
			recipient_name,
			header,
			data,
			priority,
			identifier
		};
	}

	Messenger::Message::Message(
		const std::string& sender_name,
		const std::string& recipient_name,
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority,
		const unsigned int& identifier
	) : sender_name{sender_name},
	    recipient_name{recipient_name},
	    header{header},
	    data{data},
	    priority{priority},
	    identifier{identifier} {}

	const std::string& Messenger::Message::get_sender_name() const {
		return sender_name;
	}

	const std::string& Messenger::Message::get_recipient_name() const {
		return recipient_name;
	}

	const std::string& Messenger::Message::get_header() const {
		return header;
	}

	const std::vector<std::string>& Messenger::Message::get_data() const {
		return data;
	}

	const unsigned int& Messenger::Message::get_priority() const {
		return priority;
	}

	const unsigned int& Messenger::Message::get_identifier() const {
		return identifier;
	}

	std::string Messenger::Message::serialize() const {
		std::ostringstream oss;

		oss << get_sender_name()
			<< '\0'
			<< get_recipient_name()
			<< '\0'
			<< get_header()
			<< '\0';

		for (const auto& datum : get_data())
			oss << datum << '\0';

		oss << get_priority()
			<< '\0'
			<< get_identifier()
			<< '\0';

		return oss.str();
	}

	unsigned int Messenger::Message::count{};

	unsigned int& Messenger::Message::get_count() {
		return count;
	}

	Messenger::Error::Error(const std::string& message)
		: std::system_error{errno, std::system_category(), message} {}

	void Messenger::unlink(const std::string& name) {
		unlink_message_queue(name);
	}

	Messenger::Messenger(const std::string& sender_name)
		: sender_name{sender_name} {}

	Messenger::~Messenger() {
		unlink(get_sender_name());
	}

	const std::string& Messenger::get_sender_name() const {
		return sender_name;
	}

	Messenger::Message Messenger::receive() const {
		return receive_from_message_queue(get_sender_name(), [] (
			const auto& descriptor,
			auto& raw_message,
			auto& priority
		) {
			return mq_receive(
				descriptor,
				raw_message.data(),
				raw_message.size(),
				&priority
			);
		}).value();
	}

	std::optional<Messenger::Message> Messenger::timed_receive(
		const std::chrono::high_resolution_clock::duration& timeout
	) const {
		auto absolute_timeout = convert_to_timespec(
			std::chrono::high_resolution_clock::now()
				.time_since_epoch() + timeout
		);

		return receive_from_message_queue(
			get_sender_name(),
			[&absolute_timeout] (
				const auto& descriptor,
				auto& raw_message,
				auto& priority
			) {
				return mq_timedreceive(
					descriptor,
					raw_message.data(),
					raw_message.size(),
					&priority,
					&absolute_timeout
				);
			}
		);
	}

	Messenger::Message Messenger::send(
		const std::string& recipient_name,
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) const {
		Messenger::Message message{
			get_sender_name(),
			recipient_name,
			header,
			data,
			priority
		};
		auto status = send_to_message_queue(message, [] (
			const auto& descriptor,
			const auto& raw_message,
			const auto& priority
		) {
			return mq_send(
				descriptor,
				raw_message.data(),
				raw_message.size(),
				priority
			);
		});

		if (!status)
			throw Error{
				"Message send failed due to an unknown error."
			};

		return message;
	}

	std::optional<Messenger::Message> Messenger::timed_send(
		const std::chrono::high_resolution_clock::duration& timeout,
		const std::string& recipient_name,
		const std::string& header,
		const std::vector<std::string>& data,
		const unsigned int& priority
	) const {
		Messenger::Message message{
			get_sender_name(),
			recipient_name,
			header,
			data,
			priority
		};
		auto absolute_timeout = convert_to_timespec(
			std::chrono::high_resolution_clock::now()
				.time_since_epoch() + timeout
		);
		auto status = send_to_message_queue(
			message,
			[&absolute_timeout] (
			const auto& descriptor,
			const auto& raw_message,
			const auto& priority
		) {
			return mq_timedsend(
				descriptor,
				raw_message.data(),
				raw_message.size(),
				priority,
				&absolute_timeout
			);
		});

		if (!status)
			return std::nullopt;

		return message;
	}
}
