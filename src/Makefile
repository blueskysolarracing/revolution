# Revolution Makefile

CXXFLAGS=-std=c++23

SYNCER_NAME=syncer
SYNCER_OBJECTS=logger.o messenger.o application.o topology.o instance.o

DISPLAY_DRIVER_NAME=display_driver
DISPLAY_DRIVER_OBJECTS=logger.o messenger.o application.o topology.o instance.o
MISCELLANEOUS_CONTROLLER_NAME=miscellaneous_controller
MISCELLANEOUS_CONTROLLER_OBJECTS=logger.o messenger.o application.o topology.o instance.o
MOTOR_CONTROLLER_NAME=motor_controller
MOTOR_CONTROLLER_OBJECTS=logger.o messenger.o application.o topology.o instance.o
POWER_SENSOR_NAME=power_sensor
POWER_SENSOR_OBJECTS=logger.o messenger.o application.o topology.o instance.o
TELEMETER_NAME=telemeter
TELEMETER_OBJECTS=logger.o messenger.o application.o topology.o instance.o
VOLTAGE_CONTROLLER_NAME=voltage_controller
VOLTAGE_CONTROLLER_OBJECTS=logger.o messenger.o application.o topology.o instance.o

CLIENT_NAME=client
CLIENT_OBJECTS=logger.o messenger.o application.o

NAMES=$(SYNCER_NAME) $(DISPLAY_DRIVER_NAME) $(MISCELLANEOUS_CONTROLLER_NAME) \
      $(MOTOR_CONTROLLER_NAME) $(POWER_SENSOR_NAME) $(TELEMETER_NAME) \
      $(VOLTAGE_CONTROLLER_NAME) $(CLIENT_NAME)

.PHONY: all
all: $(NAMES)
	@echo ""
	@echo "Run 'make test' to begin integration tests"
	@echo ""

.PHONY: test
test: all
	@echo "TODO: TEST"

.PHONY: clean
clean:
	-rm -f *.o $(NAMES)

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

# telemeter
$(TELEMETER_NAME): $(TELEMETER_OBJECTS)

# voltage_controller
$(VOLTAGE_CONTROLLER_NAME): $(VOLTAGE_CONTROLLER_OBJECTS)

# client
$(CLIENT_NAME): $(CLIENT_OBJECTS)
