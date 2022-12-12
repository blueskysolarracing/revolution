# Revolution

Gen 12 software for Blue Sky Solar Racing.

## Instructions

### Requirements

- systemd
- libsystemd-dev
- g++ (c++17 support)
- meson
- ninja

Below command will take care of dependencies in most systems.

Debian:

```
sudo apt install build-essential libsystemd-dev meson
pkg-config --cflags --libs libsystemd
```

### Building

At project root,

```
meson setup build
ninja -C build
```

The executables will be located under the `build/` folder.

### Integration Testing

At project root,

```
python -m unittest discover
```

### Installing

At project root,

```
sudo ninja -C build install
```

### Starting

At project root,

```
sudo ninja -C build start
```

### Stopping

At project root,

```
sudo ninja -C build stop
```

### Uninstalling

At project root,

```
sudo ninja -C build uninstall
```

## Todos

- Unit tests
- Performance tests
- Documentation (probably using sphinx)
- Improve python integration test utilities to directly use c++ stuff and mqueue
