# Revolution Makefile

CXXFLAGS=-std=c++23

SYNCER_NAME=syncer
SYNCER_OBJECTS=application.o logger.o message_queue.o topology.o

DISPLAY_DRIVER_NAME=display_driver
DISPLAY_DRIVER_OBJECTS=application.o logger.o message_queue.o topology.o
MISCELLANIOUS_CONTROLLER_NAME=miscellanious_controller
MISCELLANIOUS_CONTROLLER_OBJECTS=application.o logger.o message_queue.o topology.o
MOTOR_CONTROLLER_NAME=motor_controller
MOTOR_CONTROLLER_OBJECTS=application.o logger.o message_queue.o topology.o
POWER_SENSOR_NAME=power_sensor
POWER_SENSOR_OBJECTS=application.o logger.o message_queue.o topology.o
TELEMETER_NAME=telemeter
TELEMETER_OBJECTS=application.o logger.o message_queue.o topology.o
VOLTAGE_CONTROLLER_NAME=voltage_controller
VOLTAGE_CONTROLLER_OBJECTS=application.o logger.o message_queue.o topology.o

CLIENT_NAME=client
CLIENT_OBJECTS=application.o logger.o message_queue.o

NAMES=$(SYNCER_NAME) $(DISPLAY_DRIVER_NAME) $(MISCELLANIOUS_CONTROLLER_NAME) \
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

# miscellanious_controller
$(MISCELLANIOUS_CONTROLLER_NAME): $(MISCELLANIOUS_CONTROLLER_OBJECTS)

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
