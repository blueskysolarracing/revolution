project(
  'revolution',
  'cpp',
  version: '0.0.0',
  default_options: [
    'cpp_std=c++17',
    'optimization=3',
    'warning_level=3',
    'werror=true',
  ],
)

cpp_compiler = meson.get_compiler('cpp')

project_source_files = files(
  'src/application.cpp',
  'src/configuration.cpp',
  'src/device.cpp',
  'src/heart.cpp',
  'src/logger.cpp',
  'src/message.cpp',
  'src/peripheral.cpp',
  'src/thread_pool.cpp',
)

project_dependencies = [
  cpp_compiler.find_library('rt'),
  dependency('libgpiod'),
  dependency('libsystemd'),
  dependency('threads'),
]

database_target = executable(
  'database',
  [project_source_files, './src/database.cpp'],
  dependencies: project_dependencies,
  install: true,
)

replica_target = executable(
  'replica',
  [project_source_files, 'src/replica.cpp'],
  dependencies: project_dependencies,
  install: true,
)

display_target = executable(
  'display',
  [project_source_files, 'src/display.cpp'],
  dependencies: project_dependencies,
  install: true,
)

client_target = executable(
  'client',
  [project_source_files, 'src/client.cpp'],
  dependencies: project_dependencies,
  install: true,
)

unlinker_target = executable(
  'unlinker',
  [project_source_files, 'src/unlinker.cpp'],
  dependencies: project_dependencies,
  install: true,
)

systemd = dependency('systemd')

systemd_system_unit_dir = systemd.get_pkgconfig_variable('systemdsystemunitdir')

systemd_unit_file = configure_file(
  input: 'revolution@.service.in',
  output: 'revolution@.service',
  configuration: {
    'username': 'root',
    'bindir': get_option('prefix') / get_option('bindir'),
  },
  install_dir: systemd_system_unit_dir,
)
