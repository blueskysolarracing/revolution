librevolution_srcs = files(
  'application.cpp',
  'configuration.cpp',
  'heart.cpp',
  'logger.cpp',
  'messenger.cpp',
  'soldier.cpp',
  'worker_pool.cpp',
)

librevolution_incs = include_directories('.')

librevolution = static_library('revolution',
  librevolution_srcs,
  include_directories: librevolution_incs,
  dependencies: [threads, librt, libsystemd])
