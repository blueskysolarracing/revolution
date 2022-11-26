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

subdir('src/librevolution')

librevolution_dep = declare_dependency(
  link_with: librevolution,
  include_directories: librevolution_incs,
)

executable('marshal',
  'src/marshal.cpp',
  dependencies: [librevolution_dep])

executable('display_driver',
  'src/display_driver.cpp',
  dependencies: [librevolution_dep])

executable('miscellaneous_controller',
  'src/miscellaneous_controller.cpp',
  dependencies: [librevolution_dep])

executable('motor_controller',
  'src/motor_controller.cpp',
  dependencies: [librevolution_dep])

executable('power_sensor',
  'src/power_sensor.cpp',
  dependencies: [librevolution_dep])

executable('replica',
  'src/replica.cpp',
  dependencies: [librevolution_dep])

executable('telemeter',
  'src/telemeter.cpp',
  dependencies: [librevolution_dep])

executable('voltage_controller',
  'src/voltage_controller.cpp',
  dependencies: [librevolution_dep])

executable('client',
  'src/client.cpp',
  dependencies: [librevolution_dep])

executable('unlinker',
  'src/unlinker.cpp',
  dependencies: [librevolution_dep])
