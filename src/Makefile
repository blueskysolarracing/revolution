# Revolution Makefile

CXXFLAGS=-pedantic -std=c++17 -Wall -Wextra
LOADLIBES=-lpthread -lrt -lsystemd

MARSHAL_NAME=marshal
MARSHAL_OBJECTS=configuration.o logger.o messenger.o worker_pool.o application.o

DISPLAY_DRIVER_NAME=display_driver
DISPLAY_DRIVER_OBJECTS=\
	configuration.o \
	logger.o \
	messenger.o \
	worker_pool.o \
	application.o \
	soldier.o
MISCELLANEOUS_CONTROLLER_NAME=miscellaneous_controller
MISCELLANEOUS_CONTROLLER_OBJECTS=\
	configuration.o \
	logger.o \
	messenger.o \
	worker_pool.o \
	application.o \
	soldier.o
MOTOR_CONTROLLER_NAME=motor_controller
MOTOR_CONTROLLER_OBJECTS=\
	configuration.o \
	logger.o \
	messenger.o \
	worker_pool.o \
	application.o \
	soldier.o
POWER_SENSOR_NAME=power_sensor
POWER_SENSOR_OBJECTS=\
	configuration.o \
	logger.o \
	messenger.o \
	worker_pool.o \
	application.o \
	soldier.o
REPLICA_NAME=replica
REPLICA_OBJECTS=\
	configuration.o \
	logger.o \
	messenger.o \
	worker_pool.o \
	application.o \
	soldier.o
TELEMETER_NAME=telemeter
TELEMETER_OBJECTS=\
	configuration.o \
	logger.o \
	messenger.o \
	worker_pool.o \
	application.o \
	soldier.o
VOLTAGE_CONTROLLER_NAME=voltage_controller
VOLTAGE_CONTROLLER_OBJECTS=\
	configuration.o \
	logger.o \
	messenger.o \
	worker_pool.o \
	application.o \
	soldier.o

CLIENT_NAME=client
CLIENT_OBJECTS=messenger.o
UNLINKER_NAME=unlinker
UNLINKER_OBJECTS=configuration.o

NAMES=\
	$(MARSHAL_NAME) \
	$(DISPLAY_DRIVER_NAME) \
	$(MISCELLANEOUS_CONTROLLER_NAME) \
	$(MOTOR_CONTROLLER_NAME) \
	$(POWER_SENSOR_NAME) \
	$(REPLICA_NAME) \
	$(TELEMETER_NAME) \
	$(VOLTAGE_CONTROLLER_NAME) \
	$(CLIENT_NAME) \
	$(UNLINKER_NAME)

.PHONY: all
all: $(NAMES)

.PHONY: test
test: all

.PHONY: clean
clean:
	-rm -f *.o $(NAMES)

# marshal
$(MARSHAL_NAME): $(MARSHAL_OBJECTS)

# display_driver
$(DISPLAY_DRIVER_NAME): $(DISPLAY_DRIVER_OBJECTS)

# miscellaneous_controller
$(MISCELLANEOUS_CONTROLLER_NAME): $(MISCELLANEOUS_CONTROLLER_OBJECTS)

# motor_controller
$(MOTOR_CONTROLLER_NAME): $(MOTOR_CONTROLLER_OBJECTS)

# power_sensor
$(POWER_SENSOR_NAME): $(POWER_SENSOR_OBJECTS)

# replica
$(REPLICA_NAME): $(REPLICA_OBJECTS)

# telemeter
$(TELEMETER_NAME): $(TELEMETER_OBJECTS)

# voltage_controller
$(VOLTAGE_CONTROLLER_NAME): $(VOLTAGE_CONTROLLER_OBJECTS)

# client
$(CLIENT_NAME): $(CLIENT_OBJECTS)

# unlinker
$(UNLINKER_NAME): $(UNLINKER_OBJECTS)
