#include <cerrno>
#include <iostream>
#include <sstream>

#include "messenger.h"

namespace Revolution {
	Message Message::deserialize(const std::string &raw_message)
	{
		std::istringstream iss(raw_message);
		std::string sender_name;
		std::string header_name;
		std::string datum;
		std::vector<std::string> data;

		std::getline(iss, sender_name, '\0');
		std::getline(iss, header_name, '\0');

		while (std::getline(iss, datum, '\0'))
			data.push_back(datum);

		return Message{sender_name, header_name, data};
	}

	Message::Message(
		const std::string &sender_name,
		const std::string &header_name,
		const std::vector<std::string> &data
	) : sender_name{sender_name}, header_name{header_name}, data{data}
	{
	}

	const std::string &Message::get_sender_name() const
	{
		return sender_name;
	}

	const std::string &Message::get_header_name() const
	{
		return header_name;
	}

	const std::vector<std::string> &Message::get_data() const
	{
		return data;
	}

	std::string Message::serialize() const
	{
		std::ostringstream oss;

		oss << get_sender_name() << '\0' << get_header_name();

		for (const auto &datum : get_data())
			oss << '\0' << datum;

		return oss.str();
	}

	Messenger::Messenger(
		const std::string &name,
		const unsigned int &priority,
		Logger &logger
	) : name{name}, priority{priority}, logger{logger}
	{
	}

	Messenger::~Messenger()
	{
		for (auto &[name, descriptor] : get_descriptors()) {
			if (mq_close(descriptor) == (mqd_t) - 1)
				get_logger().log(
					Log_level::error,
					"Cannot close with message queue descriptor for " + name
					+ " (errno = " + std::to_string(errno) + ")"
				);

			if (name != get_name())
				continue;

			std::string full_name = get_full_name();

			if (mq_unlink(full_name.data()) == (mqd_t) - 1)
				get_logger().log(
					Log_level::error,
					"Cannot unlink with message queue descriptor for " + get_name()
					+ " (errno = " + std::to_string(errno) + ")"
				);
		}
	}

	const std::string &Messenger::get_name() const
	{
		return name;
	}

	const unsigned int &Messenger::get_priority() const
	{
		return priority;
	}

	Message Messenger::receive()
	{
		return receive([] (
			mqd_t &descriptor,
			std::string &raw_message,
			unsigned int &priority
		) {
			return mq_receive(
				descriptor,
				raw_message.data(),
				raw_message.size(),
				&priority
			);
		}).value();
	}

	std::optional<Message> Messenger::receive(
		const std::chrono::system_clock::time_point &timeout
	)
	{
		auto duration = timeout.time_since_epoch();
		auto seconds = std::chrono::duration_cast<std::chrono::seconds>(duration);
		auto nanoseconds = std::chrono::duration_cast<std::chrono::nanoseconds>(duration - seconds);
		auto abs_timeout = timespec{seconds.count(), nanoseconds.count()};

		return receive([&] (
			mqd_t &descriptor,
			std::string &raw_message,
			unsigned int &priority
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

	void Messenger::send(
		const std::string &recipient_name,
		const std::string &header_name,
		const std::vector<std::string> &data
	)
	{
		send(recipient_name, header_name, data, [] (
			mqd_t &descriptor,
			const std::string &raw_message,
			const unsigned int &priority
		) {
			return mq_send(
				descriptor,
				raw_message.data(),
				raw_message.size(),
				priority
			);
		});
	}

	bool Messenger::send(
		const std::chrono::system_clock::time_point &timeout,
		const std::string &recipient_name,
		const std::string &header_name,
		const std::vector<std::string> &data
	)
	{
		auto duration = timeout.time_since_epoch();
		auto seconds = std::chrono::duration_cast<std::chrono::seconds>(duration);
		auto nanoseconds = std::chrono::duration_cast<std::chrono::nanoseconds>(duration - seconds);
		auto abs_timeout = timespec{seconds.count(), nanoseconds.count()};

		return send(recipient_name, header_name, data, [&] (
			mqd_t &descriptor,
			const std::string &raw_message,
			const unsigned int &priority
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

	const std::string Messenger::name_prefix = "/revolution_";
	const int Messenger::oflags = O_RDWR | O_CREAT;
	const mode_t Messenger::mode = 0644;

	const std::string &Messenger::get_name_prefix()
	{
		return name_prefix;
	}

	const int &Messenger::get_oflags()
	{
		return oflags;
	}

	const mode_t &Messenger::get_mode()
	{
		return mode;
	}

	std::string Messenger::get_full_name(const std::string &name)
	{
		return get_name_prefix() + name;
	}

	Logger &Messenger::get_logger()
	{
		return logger;
	}

	std::unordered_map<std::string, mqd_t> &Messenger::get_descriptors()
	{
		return descriptors;
	}

	std::string Messenger::get_full_name()
	{
		return get_full_name(get_name());
	}

	mqd_t &Messenger::get_descriptor(const std::string &name)
	{
		if (get_descriptors().count(name))
			return get_descriptors()[name];

		auto &descriptor = get_descriptors()[name];
		auto full_name = get_full_name(name);

		descriptor = mq_open(
			full_name.data(),
			get_oflags(),
			get_mode(),
			NULL
		);

		if (descriptor == (mqd_t) - 1)
			get_logger().log(
				Log_level::error,
				"Cannot open with message queue descriptor for " + name
				+ " (errno = " + std::to_string(errno) + ")"
			);

		return descriptor;
	}

	std::optional<Message> Messenger::receive(
		std::function<ssize_t(mqd_t &, std::string &, unsigned int &)> receiver
	)
	{
		auto &descriptor = get_descriptor(get_name());
		mq_attr attributes;

		if (mq_getattr(descriptor, &attributes) == -1) {
			get_logger().log(
				Log_level::error,
				"Cannot get attributes with message queue descriptor for " + get_name()
				+ " (errno = " + std::to_string(errno) + ")"
			);

			return std::nullopt;
		}

		ssize_t received_size;
		std::string raw_message;
		unsigned int priority;

		raw_message.resize(attributes.mq_msgsize);

		received_size = receiver(descriptor, raw_message, priority);

		if (received_size == -1) {
			get_logger().log(
				Log_level::error,
				"Cannot receive with message queue descriptor for " + get_name()
				+ " (errno = " + std::to_string(errno) + ")"
			);

			return std::nullopt;
		}

		raw_message.resize(received_size);

		return Message::deserialize(raw_message);
	}

	bool Messenger::send(
		const std::string &recipient_name,
		const std::string &header_name,
		const std::vector<std::string> &data,
		std::function<int(mqd_t &, const std::string &, const unsigned int &)> sender
	)
	{
		Message message{get_name(), header_name, data};
		std::string raw_message{message.serialize()};

		int status = sender(
			get_descriptor(recipient_name),
			raw_message,
			get_priority()
		);

		if (status == -1)
			get_logger().log(
				Log_level::error,
				"Cannot send with message queue descriptor for " + recipient_name
				+ " (errno = " + std::to_string(errno) + ")"
			);

		return !status;
	}
}
