project(
  'revolution',
  'cpp',
  version: '0.0.0.dev0',
  default_options: [
    'warning_level=3',
    'cpp_std=c++17',
  ],
)

cpp = meson.get_compiler('cpp')

threads = dependency('threads')
librt = cpp.find_library('rt')
libsystemd = dependency('libsystemd')

dependencies = [threads, librt, libsystemd]

librevolution_srcs = files(
  'src/configuration.cpp',
  'src/heart.cpp',
  'src/logger.cpp',
  'src/messenger.cpp',
  'src/worker_pool.cpp',
  'src/application.cpp',
  'src/soldier.cpp',
)
librevolution = static_library('revolution',
  librevolution_srcs,
  dependencies: dependencies)

executable('marshal',
  'src/marshal.cpp',
  link_with: librevolution)

executable('display_driver',
  'src/display_driver.cpp',
  link_with: librevolution)

executable('miscellaneous_controller',
  'src/miscellaneous_controller.cpp',
  link_with: librevolution)

executable('motor_controller',
  'src/motor_controller.cpp',
  link_with: librevolution)

executable('power_sensor',
  'src/power_sensor.cpp',
  link_with: librevolution)

executable('replica',
  'src/replica.cpp',
  link_with: librevolution)

executable('telemeter',
  'src/telemeter.cpp',
  link_with: librevolution)

executable('voltage_controller',
  'src/voltage_controller.cpp',
  link_with: librevolution)

executable('client',
  'src/client.cpp',
  link_with: librevolution)

executable('unlinker',
  'src/unlinker.cpp',
  link_with: librevolution)
