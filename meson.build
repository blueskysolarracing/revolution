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
  dependencies: [librevolution_dep],
  install: true)

executable('display_driver',
  'src/display_driver.cpp',
  dependencies: [librevolution_dep],
  install: true)

executable('miscellaneous_controller',
  'src/miscellaneous_controller.cpp',
  dependencies: [librevolution_dep],
  install: true)

executable('motor_controller',
  'src/motor_controller.cpp',
  dependencies: [librevolution_dep],
  install: true)

executable('power_sensor',
  'src/power_sensor.cpp',
  dependencies: [librevolution_dep],
  install: true)

executable('replica',
  'src/replica.cpp',
  dependencies: [librevolution_dep],
  install: true)

executable('telemeter',
  'src/telemeter.cpp',
  dependencies: [librevolution_dep],
  install: true)

executable('voltage_controller',
  'src/voltage_controller.cpp',
  dependencies: [librevolution_dep],
  install: true)

executable('client',
  'src/client.cpp',
  dependencies: [librevolution_dep],
  install: true)

executable('unlinker',
  'src/unlinker.cpp',
  dependencies: [librevolution_dep],
  install: true)

systemd = dependency('systemd')
systemd_system_unit_dir = systemd.get_pkgconfig_variable('systemdsystemunitdir')
configure_file(
  input: 'revolution@.service.in',
  output: 'revolution@.service',
  configuration: {
    'username': 'root',
    'bindir': get_option('prefix') / get_option('bindir'),
  },
  install_dir: systemd_system_unit_dir,
)
