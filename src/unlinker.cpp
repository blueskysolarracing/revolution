#include <iostream>
#include <string>
#include <vector>

#include "messenger.h"

int main(int argc, char *argv[]) {
	std::vector<std::string> names;

	for (int i = 1; i < argc; ++i)
		names.emplace_back(argv[i]);

	for (const auto& name : names)
		try {
			Revolution::Messenger::unlink(name);
		} catch (const Revolution::Messenger::Error& error) {
			std::cerr << '('
				<< name
				<< ") "
				<< error.what()
				<< std::endl;
		}

	return 0;
}
