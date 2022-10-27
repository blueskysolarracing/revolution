# Revolution Makefile

CXXFLAGS=-std=c++17
LOADLIBES=-lrt -lpthread

SYNCER_NAME=syncer
SYNCER_OBJECTS=logger.o messenger.o configuration.o application.o master.o

DISPLAY_DRIVER_NAME=display_driver
DISPLAY_DRIVER_OBJECTS=logger.o messenger.o configuration.o application.o slave.o
MISCELLANEOUS_CONTROLLER_NAME=miscellaneous_controller
MISCELLANEOUS_CONTROLLER_OBJECTS=logger.o messenger.o configuration.o application.o slave.o
MOTOR_CONTROLLER_NAME=motor_controller
MOTOR_CONTROLLER_OBJECTS=logger.o messenger.o configuration.o application.o slave.o
POWER_SENSOR_NAME=power_sensor
POWER_SENSOR_OBJECTS=logger.o messenger.o configuration.o application.o slave.o
REPLICA_NAME=replica
REPLICA_OBJECTS=logger.o messenger.o configuration.o application.o slave.o
TELEMETER_NAME=telemeter
TELEMETER_OBJECTS=logger.o messenger.o configuration.o application.o slave.o
VOLTAGE_CONTROLLER_NAME=voltage_controller
VOLTAGE_CONTROLLER_OBJECTS=logger.o messenger.o configuration.o application.o slave.o

TERMINATOR_NAME=terminator
TERMINATOR_OBJECTS=logger.o messenger.o configuration.o

CLIENT_NAME=client
CLIENT_OBJECTS=logger.o messenger.o

NAMES=$(SYNCER_NAME) $(DISPLAY_DRIVER_NAME) $(MISCELLANEOUS_CONTROLLER_NAME) \
	$(MOTOR_CONTROLLER_NAME) $(POWER_SENSOR_NAME) $(REPLICA_NAME) \
	$(TELEMETER_NAME) $(VOLTAGE_CONTROLLER_NAME) $(TERMINATOR_NAME) \
	$(CLIENT_NAME)

.PHONY: all
all: $(NAMES)

.PHONY: test
test: all

.PHONY: clean
clean:
	-rm -f *.o *.log $(NAMES)

# syncer
$(SYNCER_NAME): $(SYNCER_OBJECTS)

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

# terminator
$(TERMINATOR_NAME): $(TERMINATOR_OBJECTS)

# client
$(CLIENT_NAME): $(CLIENT_OBJECTS)
