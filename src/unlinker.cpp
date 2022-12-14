#include <iostream>
#include <string>
#include <system_error>
#include <vector>

#include "device.h"

int main(int argc, char *argv[]) {
    std::vector<std::string> names;

    for (int i = 1; i < argc; ++i)
        names.emplace_back(argv[i]);

    for (const auto& name : names)
        try {
            Revolution::MessageQueue{'/' + name}.unlink();
        } catch (const std::system_error& error) {
            std::cerr << '('
                << name
                << ") "
                << error.what()
                << std::endl;
        }

    return 0;
}
