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

	Messenger::Message Messenger::Message::deserialize(
		const std::string& raw_message
	) {
		std::istringstream iss{raw_message};
		std::string sender_name;
		std::string recipient_name;
		std::string header;
		std::size_t datum_count;
		std::vector<std::string> data;
		unsigned int priority;
		unsigned int identifier;

		iss >> sender_name >> recipient_name >> header >> datum_count;

		data.resize(datum_count);

		for (std::size_t i{}; i < datum_count; ++i)
			iss >> data[i];

		iss >> priority >> identifier;

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
			<< ' '
			<< get_recipient_name()
			<< ' '
			<< get_header()
			<< ' '
			<< get_data().size()
			<< ' ';

		for (const auto& datum : get_data())
			oss << datum << ' ';

		oss << get_priority()
			<< ' '
			<< get_identifier()
			<< ' ';

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

	Messenger::Message Messenger::receive(
		const std::string& recipient_name
	) const {
		return receive_from_message_queue(recipient_name, [] (
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
		const std::string& recipient_name,
		const Timeout& timeout
	) const {
		auto time_point = std::chrono::high_resolution_clock::now();
		auto duration = time_point.time_since_epoch() + timeout;
		auto seconds = std::chrono::duration_cast<std::chrono::seconds>(
			duration
		);
		auto nanoseconds
			= std::chrono::duration_cast<std::chrono::nanoseconds>(
				duration - seconds
			);
		timespec abs_timeout{seconds.count(), nanoseconds.count()};

		return receive_from_message_queue(recipient_name, [&abs_timeout] (
			const auto& descriptor,
			auto& raw_message,
			auto& priority
		) {
			return mq_timedreceive(
				descriptor,
				raw_message.data(),
				raw_message.size(),
				&priority,
				&abs_timeout
			);
		});
	}

	void Messenger::send(const Message& message) const {
		send_to_message_queue(message, [] (
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
	}

	bool Messenger::timed_send(
		const Message& message,
		const Timeout& timeout
	) const {
		auto time_point = std::chrono::high_resolution_clock::now();
		auto duration = time_point.time_since_epoch() + timeout;
		auto seconds = std::chrono::duration_cast<std::chrono::seconds>(
			duration
		);
		auto nanoseconds
			= std::chrono::duration_cast<std::chrono::nanoseconds>(
				duration - seconds
			);
		timespec abs_timeout{seconds.count(), nanoseconds.count()};

		return send_to_message_queue(message, [&abs_timeout] (
			const auto& descriptor,
			const auto& raw_message,
			const auto& priority
		) {
			return mq_timedsend(
				descriptor,
				raw_message.data(),
				raw_message.size(),
				priority,
				&abs_timeout
			);
		});
	}

	const Messenger::Timeout Messenger::default_timeout{
		std::chrono::milliseconds(100)
	};

	const Messenger::Timeout& Messenger::get_default_timeout() {
		return default_timeout;
	}
}
