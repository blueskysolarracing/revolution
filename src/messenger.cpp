#include <sstream>

#include "messenger.h"

namespace Revolution {
	Messenger::Message Messenger::Message::deserialize(const std::string& raw_message)
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
		const bool& unlink,
		const unsigned int& priority,
		const int& oflags,
		const mode_t& mode
	) : name{name},
	    unlink{unlink},
	    priority{priority},
	    oflags{oflags},
	    mode{mode}
	{
	}

	Messenger::Messenger(
		const Configuration& configuration,
		Logger& logger
	) : configuration{configuration}, logger{logger}, opened_names{}
	{
		mq_unlink(get_configuration().name.data());
	}

	Messenger::~Messenger()
	{
		if (get_configuration().unlink)
			for (auto& name : get_opened_names())
				if (mq_unlink(name.data()) == (mqd_t) - 1)
					get_logger() << Logger::error
						<< "Cannot unlink with message queue descriptor for " << name
						<< " (errno = " << errno <<  ')' << std::endl;
	}

	Messenger::Message Messenger::receive()
	{
		return receive([] (
			mqd_t& descriptor,
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
		const std::chrono::system_clock::time_point& timeout
	)
	{
		auto duration = timeout.time_since_epoch();
		auto seconds = std::chrono::duration_cast<std::chrono::seconds>(duration);
		auto nanoseconds = std::chrono::duration_cast<std::chrono::nanoseconds>(duration - seconds);
		auto abs_timeout = timespec{seconds.count(), nanoseconds.count()};

		return receive([&abs_timeout] (
			mqd_t& descriptor,
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
	)
	{
		send(name, header, data, [] (
			mqd_t& descriptor,
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
		const std::chrono::system_clock::time_point& timeout,
		const std::string& name,
		const std::string& header,
		const std::vector<std::string>& data
	)
	{
		auto duration = timeout.time_since_epoch();
		auto seconds = std::chrono::duration_cast<std::chrono::seconds>(duration);
		auto nanoseconds = std::chrono::duration_cast<std::chrono::nanoseconds>(duration - seconds);
		auto abs_timeout = timespec{seconds.count(), nanoseconds.count()};

		return send(name, header, data, [&abs_timeout] (
			mqd_t& descriptor,
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

	const Messenger::Configuration& Messenger::get_configuration() const
	{
		return configuration;
	}

	Logger& Messenger::get_logger()
	{
		return logger;
	}

	const std::unordered_set<std::string>& Messenger::get_opened_names() const
	{
		return opened_names;
	}

	std::unordered_set<std::string>& Messenger::get_opened_names()
	{
		return opened_names;
	}

	mqd_t Messenger::open_descriptor(const std::string& name)
	{
		auto descriptor = mq_open(
			name.data(),
			get_configuration().oflags,
			get_configuration().mode,
			NULL
		);

		if (descriptor == (mqd_t) - 1)
			get_logger() << Logger::error
				<< "Cannot open with message queue descriptor for " << name
				<< " (errno = " << errno << ')' << std::endl;
		else
			get_opened_names().insert(name);

		return descriptor;
	}

	void Messenger::close_descriptor(const std::string& name, mqd_t& descriptor)
	{
		if (mq_close(descriptor) == (mqd_t) - 1)
			get_logger() << Logger::error
				<< "Cannot close with message queue descriptor for " << name
				<< " (errno = " << errno << ')' << std::endl;
	}

	std::optional<Messenger::Message> Messenger::receive(
		std::function<ssize_t(mqd_t&, std::string&, unsigned int&)> receiver
	)
	{
		ssize_t received_size;
		std::string raw_message;
		unsigned int priority;
		mq_attr attributes;

		auto descriptor = open_descriptor(get_configuration().name);

		if (mq_getattr(descriptor, &attributes) == -1) {
			get_logger() << Logger::error
				<< "Cannot get attributes with message queue descriptor for " << get_configuration().name
				<< " (errno = " << errno << ')' << std::endl;

			return std::nullopt;
		}

		raw_message.resize(attributes.mq_msgsize);
		received_size = receiver(descriptor, raw_message, priority);

		close_descriptor(get_configuration().name, descriptor);

		if (received_size == -1) {
			get_logger() << Logger::error
				<< "Cannot receive with message queue descriptor for " << get_configuration().name
				<< " (errno = " << errno << ')' << std::endl;

			return std::nullopt;
		}

		raw_message.resize(received_size);

		auto message = Message::deserialize(raw_message);

		get_logger() << Logger::info
			<< "Received message from " << message.sender_name << ": " << message.to_string() << std::endl;

		return message;
	}

	bool Messenger::send(
		const std::string& name,
		const std::string& header,
		const std::vector<std::string>& data,
		std::function<int(mqd_t&, const std::string&, const unsigned int&)> sender
	)
	{
		Message message{get_configuration().name, header, data};
		std::string raw_message{message.serialize()};

		auto descriptor = open_descriptor(name);

		int status = sender(
			descriptor,
			raw_message,
			get_configuration().priority
		);

		close_descriptor(name, descriptor);

		if (status == -1)
			get_logger() << Logger::error
				<< "Cannot send with message queue descriptor for " << name
				<< " (errno = " << errno << ')' << std::endl;
		else
			get_logger() << Logger::info
				<< "Sent message to " << name << ": " << message.to_string() << std::endl;

		return !status;
	}
}
