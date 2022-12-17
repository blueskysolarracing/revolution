#include <iostream>
#include <system_error>

#include "device.h"

int main(int argc, char *argv[]) {
    for (int i = 1; i < argc; ++i) {
        std::string name{argv[i]};

        try {
            Revolution::MessageQueue{'/' + name}.unlink();
        } catch (const std::system_error& error) {
            std::cerr << '('
                << name
                << ") "
                << error.what()
                << std::endl;
        }
    }

    return 0;
}
