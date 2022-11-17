# Revolution

Gen 12 software for Blue Sky Solar Racing.

## Instructions

### Requirements

- systemd
- libsystemd-dev
- g++ (supports c++17)

Below command will take care of dependencies in most systems.

Debian:

	sudo apt install build-essential libsystemd-dev
	pkg-config --cflags --libs libsystemd

### Building

At project root,

	make

### Integration Testing

At project root,

	python -m unittest discover

### Installing

At project root,

	sudo ./install.sh

### Starting

At project root,

	sudo ./start.sh

### Stopping

At project root,

	sudo ./stop.sh

### Uninstalling

At project root,

	sudo ./uninstall.sh

## Todos

- Message timestamps
- Handle empty strings properly when serializing/deserializing messages
- Unit tests
