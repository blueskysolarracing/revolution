#ifndef REVOLUTION_LOGGER_H_
#define REVOLUTION_LOGGER_H_

#include <iostream>

namespace revolution {
enum class LogLevel {
  TRACE,
  DEBUG,
  INFO,
  WARNING,
  ERROR,
  FATAL
};

typedef std::ostream Logger;
}

#endif  // REVOLUTION_LOGGER_H_
