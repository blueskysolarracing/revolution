#include <iostream>
#include <sstream>
#include <thread>

#include "client.h"

namespace Revolution {
	Client::Client(const Configuration& configuration, const std::string& recipient_name)
		: Application{configuration},
		  recipient_name{recipient_name}
	{
	}

	void Client::run()
	{
		std::thread thread{&Client::help_run, this};
		Application::run();
		thread.join();
	}

	const std::string& Client::get_recipient_name() const
	{
		return recipient_name;
	}

	void Client::help_run()
	{
		std::string input;

		while (std::getline(std::cin, input)) {
			std::istringstream iss(input);
			std::string header;
			std::string datum;
			std::vector<std::string> data;

			iss >> header;

			while (std::getline(iss, datum, ' '))
				if (!datum.empty())
					data.push_back(datum);

			if (!header.empty())
				get_messenger().send(get_recipient_name(), header, data);
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

	std::string sender_name(argv[1]);
	std::string recipient_name(argv[2]);
	Revolution::Application::Configuration configuration{
		"client",
		Revolution::Logger::Configuration{Revolution::Logger::info},
		Revolution::Messenger::Configuration{sender_name},
	};
	Revolution::Client client{configuration, recipient_name};

	client.run();

	return 0;
}
