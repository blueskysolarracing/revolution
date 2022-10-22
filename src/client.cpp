#include <iostream>
#include <sstream>
#include <thread>

#include "client.h"

namespace Revolution {
	Client::Client(const std::string &sender_name, const std::string &recipient_name)
		: Application{Instance{sender_name, get_priority(), get_log_level(), get_log_filename(), get_command(sender_name, recipient_name)}},
		  recipient_name{recipient_name}
	{
	}

	void Client::run()
	{
		std::thread thread(&Client::help_run, this);
		std::string input;

		while (std::getline(std::cin, input)) {
			std::istringstream iss(input);
			std::string header_name;
			std::string datum;
			std::vector<std::string> data;

			iss >> header_name;

			while (std::getline(iss, datum, ' '))
				if (!datum.empty())
					data.push_back(datum);

			if (!header_name.empty())
				get_messenger().send(get_recipient_name(), header_name, data);
		}
	}

	const unsigned int Client::priority{0};
	const Log_level Client::log_level{Log_level::info};
	const std::string Client::log_filename{""};

	const unsigned int &Client::get_priority()
	{
		return priority;
	}

	const Log_level &Client::get_log_level()
	{
		return log_level;
	}

	const std::string &Client::get_log_filename()
	{
		return log_filename;
	}

	const std::string Client::get_command(std::string sender_name, std::string recipient_name)
	{
		return "./client.cpp " + sender_name + " " + recipient_name;
	}

	const std::string &Client::get_recipient_name() const
	{
		return recipient_name;
	}

	void Client::help_run()
	{
		for (;;) {
			auto message = get_messenger().receive();

			std::cout << message.get_sender_name() << ": "
				<< message.get_header_name() << '(';

			auto &data = message.get_data();

			if (!data.empty()) {
				std::cout << data[0];

				for (auto it = data.begin() + 1; it != data.end(); ++it)
					std::cout << ", " << *it;
			}

			std::cout << ')' << std::endl;
		}
	}
}

int main(int argc, char *argv[])
{
	if (argc != 3) {
		std::cout << "Invalid number of arguments" << std::endl;
		std::cout << "Usage: sender_name recipient_name" << std::endl;
		return 0;
	}

	std::string senderName(argv[1]);
	std::string recipientName(argv[2]);
	Revolution::Client client{senderName, recipientName};

	client.run();

	return 0;
}
