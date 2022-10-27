#include <chrono>
#include <functional>
#include <optional>
#include <string>
#include <sstream>
#include <vector>

#include <fcntl.h>
#include <mqueue.h>
#include <sys/stat.h>

#include "logger.h"
#include "messenger.h"

namespace Revolution {
	Messenger::Message Messenger::Message::deserialize(
		const std::string& raw_message
	)
	{
		std::istringstream iss(raw_message);
		std::string sender_name;
		std::string header;
		std::string datum;
		std::vector<std::string> data;

		std::getline(iss, sender_name, '\0');
		std::getline(iss, header, '\0');

		while (std::getline(iss, datum, '\0'))
			data.push_back(datum);

		return Message{sender_name, header, data};
	}

	Messenger::Message::Message(
		const std::string& sender_name,
		const std::string& header,
		const std::vector<std::string>& data
	) : sender_name{sender_name}, header{header}, data{data}
	{
	}

	std::string Messenger::Message::serialize() const
	{
		std::ostringstream oss;

		oss << sender_name << '\0' << header << '\0';

		for (const auto& datum : data)
			oss << datum << '\0';

		return oss.str();
	}

	std::string Messenger::Message::to_string() const
	{
		std::ostringstream oss;

		oss << "Message{"
			<< "sender_name: \"" << sender_name << "\", "
			<< "header: \"" << header << "\", "
			<< "data: {";

		auto it = data.cbegin();

		if (it != data.end())
			oss << '"' << *it++ << '"';

		while (it != data.end())
			oss << ", \"" << *it++ << '"';

		oss << "}}";

		return oss.str();
	}

	Messenger::Configuration::Configuration(
		const std::string& name,
		const std::string& full_name_prefix,
		const unsigned int& priority,
		const int& oflags,
		const mode_t& mode
	) : name{name},
	    full_name_prefix{full_name_prefix},
	    priority{priority},
	    oflags{oflags},
	    mode{mode}
	{
	}

	Messenger::Messenger(
		const Configuration& configuration,
		Logger& logger
	) : configuration{configuration}, logger{logger}
	{
	}

	Messenger::Message Messenger::receive() const
	{
		return receive([] (
			const mqd_t& descriptor,
			std::string& raw_message,
			unsigned int& priority
		) {
			return mq_receive(
				descriptor,
				raw_message.data(),
				raw_message.size(),
				&priority
			);
		}).value();
	}

	std::optional<Messenger::Message> Messenger::receive(
		const std::chrono::high_resolution_clock::duration& timeout
	) const
	{
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

		return receive([&abs_timeout] (
			const mqd_t& descriptor,
			std::string& raw_message,
			unsigned int& priority
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
		const std::string& name,
		const std::string& header,
		const std::vector<std::string>& data
	) const
	{
		send(name, header, data, [] (
			const mqd_t& descriptor,
			const std::string& raw_message,
			const unsigned int& priority
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
		const std::string& name,
		const std::string& header,
		const std::vector<std::string>& data,
		const std::chrono::high_resolution_clock::duration& timeout
	) const
	{
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

		return send(name, header, data, [&abs_timeout] (
			const mqd_t& descriptor,
			const std::string& raw_message,
			const unsigned int& priority
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

	bool Messenger::send(
		const std::string& name,
		const std::string& header,
		const std::chrono::high_resolution_clock::duration& timeout
	) const
	{
		return send(name, header, {}, timeout);
	}

	const Messenger::Configuration& Messenger::get_configuration() const
	{
		return configuration;
	}

	Logger& Messenger::get_logger() const
	{
		return logger;
	}

	mqd_t Messenger::open_descriptor(const std::string& name) const
	{
		std::string full_name
			= get_configuration().full_name_prefix + name;

		auto descriptor = mq_open(
			full_name.data(),
			get_configuration().oflags,
			get_configuration().mode,
			NULL
		);

		if (descriptor == (mqd_t) - 1)
			get_logger() << Logger::error
				<< "Cannot open message queue descriptor of "
				<< name << " (errno = " << errno << ')'
				<< std::endl;

		return descriptor;
	}

	void Messenger::close_descriptor(mqd_t& descriptor) const
	{
		if (mq_close(descriptor) == (mqd_t) - 1)
			get_logger() << Logger::error
				<< "Cannot close message queue descriptor "
				<< "(errno = " << errno << ')' << std::endl;
	}

	std::optional<Messenger::Message> Messenger::receive(
		const Receiver& receiver
	) const
	{
		ssize_t received_size;
		std::string raw_message;
		unsigned int priority;
		mq_attr attributes;

		auto descriptor = open_descriptor(get_configuration().name);

		if (mq_getattr(descriptor, &attributes) == -1) {
			get_logger() << Logger::error
				<< "Cannot get message queue attributes of "
				<< get_configuration().name
				<< " (errno = " << errno << ')' << std::endl;

			return std::nullopt;
		}

		raw_message.resize(attributes.mq_msgsize);
		received_size = receiver(descriptor, raw_message, priority);

		close_descriptor(descriptor);

		if (received_size == -1) {
			get_logger() << Logger::error
				<< "Cannot receive from the message queue of "
				<< get_configuration().name
				<< " (errno = " << errno << ')' << std::endl;

			return std::nullopt;
		}

		raw_message.resize(received_size);

		auto message = Message::deserialize(raw_message);

		get_logger() << Logger::info
			<< "Successfully Received message: "
			<< message.to_string() << std::endl;

		return message;
	}

	bool Messenger::send(
		const std::string& name,
		const std::string& header,
		const std::vector<std::string>& data,
		const Sender& sender
	) const
	{
		Message message{get_configuration().name, header, data};
		std::string raw_message{message.serialize()};

		auto descriptor = open_descriptor(name);

		int status = sender(
			descriptor,
			raw_message,
			get_configuration().priority
		);

		close_descriptor(descriptor);

		if (status == -1)
			get_logger() << Logger::error
				<< "Cannot send to the message queue of "
				<< name << " (errno = " << errno << ')'
				<< std::endl;
		else
			get_logger() << Logger::info
				<< "Successfully Sent message to "
				<< name << ": " << message.to_string()
				<< std::endl;

		return !status;
	}
}
