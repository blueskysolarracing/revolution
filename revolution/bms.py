from enum import Enum
import queue
from dataclasses import dataclass, field
import numpy as np
from periphery import SPI, GPIO
from threading import Lock
import time
import math
from revolution.worker import Worker

###### battery_config.h & bms_module.h  constants ######

BMS_DISCONNECTED_VOLTAGE_THRESHOLD = 6.0
BMS_DISCONNECTED_TEMPERATURE_THRESHOLD = -100.0

HV_BATT_OC_THRESHOLD = 60.0 	#Should be set to 60.0A
HV_BATT_OV_THRESHOLD = 4.25  #Should be set to 4.25V
HV_BATT_UV_THRESHOLD = 2.50	#Should be set to 2.50V
HV_BATT_OT_THRESHOLD = 60.0 	#Should be set to 60.0C
HV_BATT_UT_THRESHOLD = 0.0   #Should be set to 0.0C

BMS_MODULE_NUM_STATE_OF_CHARGES = BMS_MODULE_NUM_VOLTAGES = NUM_CELLS_PER_MODULE = 5
BMS_NUM_BMS_MODULES = NUM_BMS_MODULES	= 6 #Number of BMS modules to read from
NUM_BATT_CELLS = NUM_BMS_MODULES*NUM_CELLS_PER_MODULE #Number of series parallel groups in battery pack
BMS_MODULE_NUM_TEMPERATURES = BMS_MODULE_NUM_TEMPERATURE_SENSOR = NUM_TEMP_SENSORS_PER_MODULE = 3 
NUM_BATT_TEMP_SENSORS =	NUM_TEMP_SENSORS_PER_MODULE*NUM_BMS_MODULES #Number of temperature sensors in battery pack	


BATTERY_CELL_VOLTAGES_INITIAL_VALUE = -1000.0
BATTERY_CELL_VOLTAGES_FAKE_VALUE = 0.0
BATTERY_TEMPERATURES_INITIAL_VALUE = -1000.0
BATTERY_SOC_INITIAL_VALUE = -1000.0

MAX_ALLOWD_OVERCURRENT_TIME = 7000 # 7 seconds
MOTOR_OT_THRESHOLD = 180.0 # 180.0C
MOTOR_OT_WARNING_THRESHOLD =  100.0 # 100.0C 

HV_BATT_OV_DEBOUNCE_TIME  = 3000 # 3 seconds
HV_BATT_UV_DEBOUNCE_TIME =  3000 # 3 seconds

FLOAT_QUEUE_NUM_VALUES = 20

# From batteryEKF.h
STATE_NUM = 3
INPUT_NUM = 2
OUTPUT_NUM = 1

R_D = R_CT = 0.00294294 # in Ohm
C_D = C_CT = 2072.89471 # in Farad

Q_CAP = 173880.0 # in Ampere Second  49 Ampere hour = 49*3600 = 176400 Ampere Second
COULOMB_ETA = 1.0



###### end of battery_config.h & bms_module.h constants ######

###### classes translated from bms_module.h, cQueue.h, batteryEKF.h ######

class GetMode(Enum):
    GET_MOST_RECENT = 1
    GET_PAST_AVERAGE = 2
    GET_FILTERED_RESULT = 3

class GPIO_PinState(Enum): 
    GPIO_PIN_RESET = 0
    GPIO_PIN_SET = 1

# Custom implementation of Queue for thread-safe operations and overwriting
class CustomQueue(queue.Queue):
    def __init__(self, maxsize=0, overwrite=False) -> None:
        super().__init__(maxsize)
        self.overwrite = overwrite

    def put(self, item, block=True, timeout=None) -> None:
        with self.not_full:
            if self.overwrite and self.full():
                with self.mutex:
                    self._get() 
            super().put(item, block, timeout)

    def peek(self):
        if self.empty():
            raise queue.Empty
        with self.mutex:
            
            return self.queue[0]

    def drop(self) -> None:
        if self.empty():
            raise queue.Empty
        with self.mutex:
            self.queue.popleft()

    def peek_index(self, index : int):
        with self.mutex:
            if index >= self.qsize():
                raise IndexError("Index out of range")
            return self.queue[index]

    def get_size(self) -> int:
        with self.mutex:
            return self.qsize()
        
    def get_avg(self) -> float:
        with self.mutex:
            if self.empty():
                raise queue.Empty
            return sum(self.queue) / self.qsize()
            
class FloatQueue(CustomQueue):
    def __init__(self) -> None:
        super().__init__(FLOAT_QUEUE_NUM_VALUES, True)




# from batteryEKF.h

class EKFModelMatrix:
    # -------------- CONSTANTS AND EKF ALGO VARIABLES --------------
    dim1: np.ndarray = np.zeros(2, dtype=np.uint8)
    dim2: np.ndarray = np.zeros(2, dtype=np.uint8)
    dim3: np.ndarray = np.zeros(2, dtype=np.uint8)
    dim4: np.ndarray = np.zeros(2, dtype=np.uint8)
    dim5: np.ndarray = np.zeros(2, dtype=np.uint8)
    dim6: np.ndarray = np.zeros(2, dtype=np.uint8)
    dim7: np.ndarray = np.zeros(2, dtype=np.uint8)

    # a priori state covariance matrix - k+1|k (prediction)
    P_k: np.ndarray = np.zeros(STATE_NUM * STATE_NUM, dtype=np.float32)
    # noise in state measurement (sampled) - expected value of the distribution
    Q: np.ndarray = np.zeros(STATE_NUM * STATE_NUM, dtype=np.float32)
    # noise in output sensor (sampled) - expected value of the distribution
    R: np.ndarray = np.zeros(OUTPUT_NUM, dtype=np.float32)
    # a priori measurement covariance
    S: np.ndarray = np.zeros(OUTPUT_NUM, dtype=np.float32)
    # Kalman Weight
    W: np.ndarray = np.zeros(STATE_NUM * OUTPUT_NUM, dtype=np.float32)

    covList: np.ndarray = np.zeros(STATE_NUM, dtype=np.float32)
    A: np.ndarray = np.zeros(STATE_NUM * STATE_NUM, dtype=np.float32)
    B: np.ndarray = np.zeros(STATE_NUM * INPUT_NUM, dtype=np.float32)
    C: np.ndarray = np.zeros(STATE_NUM * OUTPUT_NUM, dtype=np.float32)
    D: np.ndarray = np.zeros(INPUT_NUM, dtype=np.float32)

    U: np.ndarray = np.zeros(INPUT_NUM, dtype=np.float32)
    V_Measured: np.ndarray = np.zeros(1, dtype=np.float32)
    V_OCV: np.ndarray = np.zeros(1, dtype=np.float32)

    # ------------- HELPER VARIABLES TO COMPUTE INVERSES -------------
    A_T: np.ndarray = np.zeros(STATE_NUM * STATE_NUM, dtype=np.float32)
    A_P: np.ndarray = np.zeros(STATE_NUM * STATE_NUM, dtype=np.float32)
    A_P_AT: np.ndarray = np.zeros(STATE_NUM * STATE_NUM, dtype=np.float32)
    P_k1: np.ndarray = np.zeros(STATE_NUM * STATE_NUM, dtype=np.float32)

    C_T: np.ndarray = np.zeros(STATE_NUM * OUTPUT_NUM, dtype=np.float32)
    C_P: np.ndarray = np.zeros(STATE_NUM * OUTPUT_NUM, dtype=np.float32)
    C_P_CT: np.ndarray = np.zeros(OUTPUT_NUM * OUTPUT_NUM, dtype=np.float32)

    SInv: np.ndarray = np.zeros(OUTPUT_NUM * OUTPUT_NUM, dtype=np.float32)

    P_CT: np.ndarray = np.zeros(STATE_NUM * OUTPUT_NUM, dtype=np.float32)

    W_T: np.ndarray = np.zeros(OUTPUT_NUM * STATE_NUM, dtype=np.float32)
    W_S: np.ndarray = np.zeros(STATE_NUM * OUTPUT_NUM, dtype=np.float32)
    W_S_WT: np.ndarray = np.zeros(STATE_NUM * STATE_NUM, dtype=np.float32)

    A_X: np.ndarray = np.zeros(STATE_NUM, dtype=np.float32)
    B_U: np.ndarray = np.zeros(STATE_NUM * INPUT_NUM, dtype=np.float32)
    CX_DU: np.ndarray = np.zeros(OUTPUT_NUM, dtype=np.float32)
    X_k1: np.ndarray = np.zeros(STATE_NUM, dtype=np.float32)
    Z_k1: np.ndarray = np.zeros(OUTPUT_NUM, dtype=np.float32)

    C_X: np.ndarray = np.zeros(OUTPUT_NUM, dtype=np.float32)
    D_U: np.ndarray = np.zeros(OUTPUT_NUM, dtype=np.float32)

    Z_err: np.ndarray = np.zeros(OUTPUT_NUM, dtype=np.float32)
    W_Zerr: np.ndarray = np.zeros(STATE_NUM, dtype=np.float32)

class EKF_Model_14p:
    covP : list[float] = field(default_factory = lambda: [0.0] * (STATE_NUM * STATE_NUM))
    matrix : EKFModelMatrix

    # Incomplete constructor. This replaces initEKFModel and initBatteryAlgo
    def __init__(self, initial_v : float, initial_deltaT : float) -> None:

        self.stateX : list[float] = [0.0] * STATE_NUM
        self.covP : list[float] = [0.0] * (STATE_NUM * STATE_NUM)
        self.matrix = EKFModelMatrix()
        # pass



    def run_EKF(self, dt : float, currentIn : float, measuredV : float) -> None:
        pass

    def compute_A_B_dt(self, dt : float) -> None:

        self.matrix.A[0] = 1.0
        self.matrix.A[4] = np.exp(-dt/(R_CT*C_CT))
        self.matrix.A[8] = np.exp(-dt/(R_D*C_D))

        self.matrix.B[0] = ((-COULOMB_ETA) * dt / Q_CAP) 
        self.matrix.B[2] = 1 - np.exp(-dt/(R_CT*C_CT))
        self.matrix.B[3] = 1 - np.exp(-dt/(R_D*C_D))    


        pass    


@dataclass
class BmsModule:  

    
    _bms_module_id : int
    _spi_handle : SPI
    _spi_cs_port : GPIO # Should be initialized with pin
    # _spi_cs_pin : int

    init_flag : int = 0 # not sure if this is necessary
    current : float = 0.0

    _voltages : list[float] = field(default_factory= lambda: [0.0] * BMS_MODULE_NUM_VOLTAGES)   
    past_voltages : list[FloatQueue] = field(default_factory= lambda: [FloatQueue() for i in range(BMS_MODULE_NUM_VOLTAGES)] )  

    _temperatures : list[float] = field(default_factory= lambda: [0.0] * BMS_MODULE_NUM_TEMPERATURES)
    past_temperatures : list[FloatQueue] = field(default_factory= lambda: [FloatQueue() for i in range(BMS_MODULE_NUM_TEMPERATURES)] )

    _state_of_charges  : list[float] = field(default_factory= lambda: [0.0] * BMS_MODULE_NUM_STATE_OF_CHARGES)
    _EKF_models : list[EKF_Model_14p] = []
    _tick_last_soc_compute : list[int] = field(default_factory= lambda: [0] * BMS_MODULE_NUM_STATE_OF_CHARGES)
    

    def __post_init__(self) -> None:   

        #  for simulating suspension of tasks
        self.lock = Lock()

        self._spi_cs_port.write(GPIO_PinState.GPIO_PIN_SET)
        
        for i in range(BMS_MODULE_NUM_VOLTAGES):
            self.past_voltages[i] = FloatQueue()
            self._state_of_charges[i] = BATTERY_SOC_INITIAL_VALUE
            self._voltages[i] = BATTERY_CELL_VOLTAGES_FAKE_VALUE
        
        for i in range(BMS_MODULE_NUM_TEMPERATURES):
            self.past_temperatures[i] = FloatQueue()
            self._temperatures[i] = BATTERY_TEMPERATURES_INITIAL_VALUE

        # we want to measure many times to ensure we initialize SOC with a filtered voltage
        for i in range(10):
            self.measure_voltage()
            self.measure_temperature()

        # SOC Algorithm
        for i in range(BMS_MODULE_NUM_STATE_OF_CHARGES):
            self._tick_last_soc_compute[i] = get_tick_count()
            self._EKF_models.append(EKF_Model_14p(self.past_voltages[i].get_avg(), self._tick_last_soc_compute))  

        self.compute_soc()

    @staticmethod
    def LTC6810_convert_to_temp(input_voltage : list[float], output_temperature : list[float]) -> None:
        pass

    @staticmethod
    def LTC6810_command_generate_address_mode(command : int, data_to_send : list[int], address : int) -> None:
        address_command = (0b10000 | (address & 0b1111)) << 11
        command |= address_command
        BmsModule.LTC6810_command_generate(command, data_to_send)

    @staticmethod
    def LTC6810_command_generate(command : int, data_to_send : list[int]) -> None:
        CMD0_list = [0] * 8
        CMD1_list = [0] * 8  # [7] is MSB, [0] is LSB
        # Convert command and fill the two above arrays
        BmsModule.LTC6810_command_to_list(command, CMD0_list, CMD1_list)

        # Now generate error checking bits
        PEC_bits0 = [0] * 8
        PEC_bits1 = [0] * 8

        BmsModule.LTC6810_generate_pec_bits(CMD0_list, CMD1_list, PEC_bits0, PEC_bits1)

        # Put them back into the data_to_send array, with size of 4
        data_to_send[0] = BmsModule.LTC6810_list_to_byte(CMD0_list)  # 1st byte message
        data_to_send[1] = BmsModule.LTC6810_list_to_byte(CMD1_list)  # 2nd byte message
        data_to_send[2] = BmsModule.LTC6810_list_to_byte(PEC_bits0)  # 1st byte error check
        data_to_send[3] = BmsModule.LTC6810_list_to_byte(PEC_bits1)  # 2nd byte error check

    @staticmethod
    def LTC6810_command_to_list(command : int, CMD0_ref : list[int], CMD1_ref : list[int]) -> None:

        for i in range(16):  # from LSB to MSB, fill CMD1 first
            temp_bit = command % 2
            if i <= 7:
                CMD1_ref[i] = temp_bit
            else:
                CMD0_ref[i - 8] = temp_bit
            command = command >> 1 


    @staticmethod
    def LTC6810_generate_PEC_bits_6byte(data6Byte : list[int], PCE0 : list[int], PCE1 : list[int]) -> None:
        # Note: data6Byte[74] is 1st bit

        # Refer to P55 of LTC
        IN0 = IN3 = IN4 = IN7 = IN8 = IN10 = IN14 = 0  # Initialize all polynomial stuff to 0

        PEC = [0] * 15
        PEC[4] = 1
        # Above initializes the 15 bit PEC. In the last cycle shift up add 0 at LSB

        # Count Din from most significant bit
        for i in range(47, -1, -1):  # Do the shifting and stuff
            DIN = data6Byte[i]

            # Now DIN is assigned, do step 2 which is shifting
            IN0 = DIN ^ PEC[14]
            IN3 = IN0 ^ PEC[2]
            IN4 = IN0 ^ PEC[3]
            IN7 = IN0 ^ PEC[6]
            IN8 = IN0 ^ PEC[7]
            IN10 = IN0 ^ PEC[9]
            IN14 = IN0 ^ PEC[13]

            # Step 3, shift
            PEC[14] = IN14
            PEC[13] = PEC[12]
            PEC[12] = PEC[11]
            PEC[11] = PEC[10]
            PEC[10] = IN10
            PEC[9] = PEC[8]
            PEC[8] = IN8
            PEC[7] = IN7
            PEC[6] = PEC[5]
            PEC[5] = PEC[4]
            PEC[4] = IN4
            PEC[3] = IN3
            PEC[2] = PEC[1]
            PEC[1] = PEC[0]
            PEC[0] = IN0

        for j in range(14, -1, -1):
            if j >= 7:
                PCE0[j - 7] = PEC[j]
            else:
                PCE1[j + 1] = PEC[j]

        # Now add a 0 at the end and stuff it into 2 bytes
        PCE1[0] = 0



    @staticmethod
    def LTC6810_generate_pec_bits(CMD0 : list[int], CMD1 : list[int], PCE0 : list[int], PCE1 : list[int]) -> None:
        # Refer to P55 of LTC
        IN0 = IN3 = IN4 = IN7 = IN8 = IN10 = IN14 = 0  # Initialize all polynomial stuff to 0

        PEC = [0] * 15
        PEC[4] = 1
        # Above initializes the 15 bit PEC. In the last cycle shift up add 0 at LSB

        # Count Din from most significant bit
        for i in range(15, -1, -1):  # Do the shifting and stuff
            if i >= 8:  # Grab DIN from CMD0
                DIN = CMD0[i - 8]
            else:
                DIN = CMD1[i]

            # Now DIN is assigned, do step 2 which is shifting
            IN0 = DIN ^ PEC[14]
            IN3 = IN0 ^ PEC[2]
            IN4 = IN0 ^ PEC[3]
            IN7 = IN0 ^ PEC[6]
            IN8 = IN0 ^ PEC[7]
            IN10 = IN0 ^ PEC[9]
            IN14 = IN0 ^ PEC[13]

            # Step 3, shift
            PEC[14] = IN14
            PEC[13] = PEC[12]
            PEC[12] = PEC[11]
            PEC[11] = PEC[10]
            PEC[10] = IN10
            PEC[9] = PEC[8]
            PEC[8] = IN8
            PEC[7] = IN7
            PEC[6] = PEC[5]
            PEC[5] = PEC[4]
            PEC[4] = IN4
            PEC[3] = IN3
            PEC[2] = PEC[1]
            PEC[1] = PEC[0]
            PEC[0] = IN0

        for j in range(14, -1, -1):
            if j >= 7:
                PCE0[j - 7] = PEC[j]
            else:
                PCE1[j + 1] = PEC[j]

        # Now add a 0 at the end and stuff it into 2 bytes
        PCE1[0] = 0
    


    @staticmethod
    def LTC6810_list_to_byte(input_list : list[int]) -> int:
        output_byte = 0
        i = 7
        # Note: [7] is MSB, [0] is LSB.
        while i >= 1:
            output_byte = output_byte + input_list[i]
            output_byte = output_byte * 2  # left shift one bit
            i -= 1
            # Note: array_in[i] shall be either 1 or 0.
        output_byte = output_byte + input_list[i]  # put last bit in
        return output_byte
    
    @staticmethod
    def LTC6810VoltageDataConversion(low_byte : int, high_byte : int) -> int:
        # Based on LTC6810 datasheet, every bit is 100uV
        # Full range of 16 bytes: -0.8192 to +5.7344
        # Final voltage: (total - 8192) * 100uV
        voltage = low_byte + high_byte * 256
        # voltage = voltage + 8192
        return voltage
    
    @staticmethod
    def LTC6810_convert_to_temp(input_voltage : list[float], output_temperature : list[float]) -> None:
        # Used to convert raw ADC code to temperature
        temp_correction_multiplier = 1.0
        temp_correction_offset = 0.0
        BMS_MODULE_NUM_TEMPERATURES = 3
        
        for i in range(BMS_MODULE_NUM_TEMPERATURES):
            corrected_voltage = temp_correction_multiplier * (input_voltage[i] / 10000.0 - temp_correction_offset)
            thermistor_resistance = 10.0 / ((2.8 / corrected_voltage) - 1.0)
            output_temperature[i] = 1.0 / (0.003356 + 0.0002532 * math.log(thermistor_resistance / 10.0))
            output_temperature[i] = output_temperature[i] - 273.15

            if thermistor_resistance < 0:  # Preventing NaN (treated as 0xFFFFFFFF) from tripping the battery safety but lower-bounding them to -100C
                output_temperature[i] = -100
            # This occurs when the measurement is close to 3V, suggesting that the thermistor isn't connected.
    


    def LTC6810_transmit_isospi_mode(self, data : list[int]) -> None:

        self.LTC6810_isospi_wakeup()
        time.sleep(0.001)
        self._spi_cs_port.write(GPIO_PinState.GPIO_PIN_RESET)
        time.sleep(0.001)
        self._spi_handle.transfer(data)
        self._spi_cs_port.write(GPIO_PinState.GPIO_PIN_SET)

        pass

    def LTC6810_transmit_receive_isospi_mode(self, data_to_send : list[int], data_to_receive : list[int]) -> None:
        self.LTC6810_isospi_wakeup()
        time.sleep(0.001)
        self._spi_cs_port.write(GPIO_PinState.GPIO_PIN_RESET)
        time.sleep(0.001)
        self._spi_handle.transfer(data_to_send)
        time.sleep(0.001)
        received_datalist = self._spi_handle.transfer([0x00] * len(data_to_receive))
        for i, data in enumerate(received_datalist):
            data_to_receive[i] = data   
        time.sleep(0.001)
        self._spi_cs_port.write(GPIO_PinState.GPIO_PIN_SET)

        


    def LTC6810_init(self, GPIO4 : int, GPIO3 : int, GPIO2 : int, DCC5 : int, DCC4 : int, DCC3 : int, DCC2 : int, DCC1 : int) -> None:

        """This function initialize the LTC6810 ADC chip, shall be called at the start of the program
        
        To modify the initialization setting, please refer to the Datasheet and the chart below:

        +-------+---------+---------+---------+---------+---------+---------+---------+--------+
        | reg   | Bit7    | Bit6    | Bit5    | Bit4    | Bit3    | Bit2    | Bit1    | Bit0   |
        +-------+---------+---------+---------+---------+---------+---------+---------+--------+
        | CFGR0 | RSVD    | GPIO4   | GPIO3   | GPIO2   | GPIO1   | REFON   | DTEN    | ADCOPT |
        +-------+---------+---------+---------+---------+---------+---------+---------+--------+
        | CFGR1 | VUV[7]  | VUV[6]  | VUV[5]  | VUV[4]  | VUV[3]  | VUV[2]  | VUV[1]  | VUV[0] |
        +-------+---------+---------+---------+---------+---------+---------+---------+--------+
        | CFGR2 | VOV[3]  | VOV[2]  | VOV[1]  | VOV[0]  | VUV[11] | VUV[10] | VUV[9]  | VUV[8] |
        +-------+---------+---------+---------+---------+---------+---------+---------+--------+
        | CFGR3 | VOV[11] | VOV[10] | VOV[9]  | VOV[8]  | VOV[7]  | VOV[6]  | VOV[5]  | VOV[4] |
        +-------+---------+---------+---------+---------+---------+---------+---------+--------+
        | CFGR4 | DCC0    | MCAL    | DCC6    | DCC5    | DCC4    | DCC3    | DCC2    | DCC1   |
        +-------+---------+---------+---------+---------+---------+---------+---------+--------+
        | CFGR5 | DCTO[3] | DCTO[2] | DCTO[1] | DCTO[0] | SCONV   | FDRF    | DIS_RED | DTMEN  |
        +-------+---------+---------+---------+---------+---------+---------+---------+--------+


        connection to MUX for thermal measurements:
        GPIO2 -> A0
        GPIO3 -> A1
        GPIO4 -> A2
        GPIO1 shall always be set to 1 to avoid internal pull-down, as its the voltage reading pin.
        A2 is MSB and A0 is MSB, if want channel 2 -> do A2=0, A1=1, A0=0
        above is the table of configuration register bits."""

        data6byte = [0] * 48 # [47] is MSB, CFGR0 Bit7 
        data_to_send = [0] * 12 

        # Write configure command
        message_in_binary = 0b1
        self.LTC6810_command_generate_address_mode(message_in_binary, data_to_send, self._bms_module_id)

        #set GPIO bits to 1 so they aren`t being pulled down internally by the chip.
        #set REFON to enable the 3V that goes to the chip
        #DTEN to 1 to enable discharge timer
        #ADCOPT bit to 0, use 422Hz as its stable
        #above are byte0, byte 1 full of 0s as VUV currently not used.
        message_in_binary = 0b0000110000000000

        # now add the GPIO config
        message_in_binary = message_in_binary + 4096 * GPIO2 + 8192 * GPIO3 + 16384 * GPIO4

        MSG0 = [0] * 8
        MSG1 = [0] * 8 
        self.LTC6810_command_to_list(message_in_binary, MSG0, MSG1)

        for i in range(7, -1, -1):
            data6byte[40 + i] = MSG0[i]
            data6byte[32 + i] = MSG1[i]

        # Set the VOV and VUV as 0
        message_in_binary = 0b0000000000000000
        MSG2 = [0] * 8
        MSG3 = [0] * 8

        self.LTC6810_command_to_list(message_in_binary, MSG2, MSG3) 
        for i in range(7, -1, -1):
            data6byte[24 + i] = MSG2[i]
            data6byte[16 + i] = MSG3[i] 

        #DCC = 0: discharge off, 1: discharge = on
        #MCAL = 1: enable multi-calibration. for this don`t use, turn to 0
        #DCTO: discharge timer. for now 0
        #SCONV: redundant measurement using S pin, disable for now (0)
        #FDRF: not using it anyway, to 0
        #DIS_RED: redundancy disable: set to 1 to disable
        #DTMEN: Discharge timer monitor, 0 to disable
        message_in_binary = 0b0000000000000010
        message_in_binary = message_in_binary + 256 * DCC1 + 512 * DCC2 + 1024 * DCC3 + 2048 * DCC4 + 4096 * DCC5 
        
        MSG4 = [0] * 8
        MSG5 = [0] * 8 
        self.LTC6810_command_to_list(message_in_binary, MSG4, MSG5)
        for i in range(7, -1, -1):
            data6byte[8 + i] = MSG4[i]
            data6byte[i] = MSG5[i]

        # Now create PEC bits based on above data

        PEC0_6 = [0] * 8
        PEC1_6 = [0] * 8

        self.LTC6810_generate_PEC_bits_6byte(data6byte, PEC0_6, PEC1_6) 

        data_to_send[4] = self.LTC6810_list_to_byte(MSG0)
        data_to_send[5] = self.LTC6810_list_to_byte(MSG1)
        data_to_send[6] = self.LTC6810_list_to_byte(MSG2)
        data_to_send[7] = self.LTC6810_list_to_byte(MSG3)
        data_to_send[8] = self.LTC6810_list_to_byte(MSG4)
        data_to_send[9] = self.LTC6810_list_to_byte(MSG5)
        data_to_send[10] = self.LTC6810_list_to_byte(PEC0_6)
        data_to_send[11] = self.LTC6810_list_to_byte(PEC1_6)

        self.LTC6810_transmit_isospi_mode(data_to_send)
        pass

    def LTC6810_isospi_wakeup(self) -> None:
        self._spi_cs_port.write(GPIO_PinState.GPIO_PIN_RESET)
        self._spi_handle.transfer([0x00])
        self._spi_cs_port.write(GPIO_PinState.GPIO_PIN_SET) 


    def LTC6810_read_temp(self, temp_list : list[float], DCC5 : int, DCC4 : int, DCC3 : int, DCC2 : int, DCC1 : int) -> None:
        

        data_to_send = [0] * 16
        data_to_receive = [0] * 8

        for cycle in range(3):

            if cycle == 0: #channel 3
                self.LTC6810_init(0, 1, 1, DCC5, DCC4, DCC3, DCC2, DCC1)
            elif cycle == 1: # channel 4
                self.LTC6810_init(1, 0, 0, DCC5, DCC4, DCC3, DCC2, DCC1)
            elif cycle == 2: # channel 5
                self.LTC6810_init(1, 0, 1, DCC5, DCC4, DCC3, DCC2, DCC1)

            message_in_binary = 0b10100010010 # conversion GPIO1, command AXOW
            self.LTC6810_command_generate_address_mode(message_in_binary, data_to_send, self._bms_module_id)
            self.LTC6810_transmit_isospi_mode(data_to_send)

            message_in_binary = 0b1100 # read auxiliary group 1, command RDAUXA
            self.LTC6810_command_generate_address_mode(message_in_binary, data_to_send, self._bms_module_id)
            self.LTC6810_transmit_receive_isospi_mode(data_to_send, data_to_receive)

            temp_sum = 256 * data_to_receive[3] + data_to_receive[2]

            temp_list[cycle] = float(temp_sum)

    
    def LTC6810_read_volt(self, volt_list : list[float]) -> None:
        
        data_to_send = [0] * 4
        data_to_receive = [0] * 8

        v_message_in_binary = 0b01101110000
        self.LTC6810_command_generate_address_mode(v_message_in_binary, data_to_send, self._bms_module_id)
        self.LTC6810_transmit_receive_isospi_mode(data_to_send, data_to_receive)

        time.sleep(ticks_to_s(10))

        v_message_in_binary = 0b100
        self.LTC6810_command_generate_address_mode(v_message_in_binary, data_to_send, self._bms_module_id)
        self.LTC6810_transmit_receive_isospi_mode(data_to_send, data_to_receive)

        volt_list[0] = self.LTC6810VoltageDataConversion(data_to_receive[0], data_to_receive[1]) /10000.0
        volt_list[1] = self.LTC6810VoltageDataConversion(data_to_receive[2], data_to_receive[3]) /10000.0
        volt_list[2] = self.LTC6810VoltageDataConversion(data_to_receive[4], data_to_receive[5]) /10000.0

        v_message_in_binary = 0b110
        self.LTC6810_command_generate_address_mode(v_message_in_binary, data_to_send, self._bms_module_id)  
        self.LTC6810_transmit_receive_isospi_mode(data_to_send, data_to_receive)

        volt_list[3] = self.LTC6810VoltageDataConversion(data_to_receive[0], data_to_receive[1]) /10000.0
        volt_list[4] = self.LTC6810VoltageDataConversion(data_to_receive[2], data_to_receive[3]) /10000.0


    
    # retrieves temperature in place from member variables
    def get_temperature(self, temperatures : list[float], mode: GetMode) -> None:

        with self.lock:
            for i in range(BMS_MODULE_NUM_TEMPERATURES):
                if mode == GetMode.GET_MOST_RECENT:
                    temperatures[i] = self._temperatures[i]
                elif mode == GetMode.GET_PAST_AVERAGE:
                    if check_temperature_is_valid(self._temperatures[i]): 
                        temperatures[i] = self.past_temperatures[i].get_avg()
                    else:
                        temperatures[i] = BATTERY_TEMPERATURES_INITIAL_VALUE
                elif mode == GetMode.GET_FILTERED_RESULT:   
                    # Can consider running past temperatures through Moving Average Filter, not necessary for now
                    pass



    # retrieves temperature in place from member variables
    def get_voltage(self, voltages : list[float], mode : GetMode) -> None:

        with self.lock:
            for i in range(BMS_MODULE_NUM_VOLTAGES):
                if mode == GetMode.GET_MOST_RECENT:
                    voltages[i] = self._voltages[i]
                elif mode == GetMode.GET_PAST_AVERAGE:
                    if check_voltage_is_valid(self._voltages[i])   :
                        voltages[i] = self.past_voltages[i].get_avg()
                    else:
                        voltages[i] = BATTERY_CELL_VOLTAGES_INITIAL_VALUE
                elif mode == GetMode.GET_FILTERED_RESULT:
                    # Can consider running past voltages through Moving Average Filter, not necessary for now
                    pass


    def get_state_of_charge(self, state_of_charges : list[float], mode : GetMode) -> None:
        with self.lock:
            for i in range(BMS_MODULE_NUM_STATE_OF_CHARGES):
                state_of_charges[i] = self._state_of_charges[i]

    # Accesses hardware and stores the measured temperature into member variables
    def measure_temperature(self) -> None:

        local_temp_list = [0.0] * BMS_MODULE_NUM_TEMPERATURES  

        # reads voltage and converts to temp
        self.LTC6810_read_temp(local_temp_list, 0, 0, 0, 0, 0)
        self.LTC6810_convert_to_temp(local_temp_list, local_temp_list)

        with self.lock:
            for i in range(BMS_MODULE_NUM_TEMPERATURES):
                if check_temperature_is_valid(local_temp_list[i]):
                    self._temperatures[i] = local_temp_list[i]
                    self.past_temperatures[i].put(local_temp_list[i])
                else:
                    # If temperature is invalid, assume bms module is not connected, and don't push to queue
                    self._temperatures[i] = BATTERY_TEMPERATURES_INITIAL_VALUE
            

    # Accesses hardware and stores the measured voltage into member variables
    def measure_voltage(self) -> None:

        local_voltage_list = [0.0] * BMS_MODULE_NUM_VOLTAGES   
        self.LTC6810_read_volt(local_voltage_list)

        with self.lock:

            for i in range(BMS_MODULE_NUM_VOLTAGES):
                if check_voltage_is_valid(local_voltage_list[i]):
                    self._voltages[i] = local_voltage_list[i]
                    self.past_voltages[i].put(self._voltages[i])
                else:
                    # If voltage is invalid, assume bms module is not connected, and don't push to queue
                    self._voltages = BATTERY_CELL_VOLTAGES_INITIAL_VALUE

    # Accesses hardware and computes the measured soc, stores into member variables
    def compute_soc(self) -> None:

        local_soc_list = [0.0] * BMS_MODULE_NUM_STATE_OF_CHARGES

        for i in range(BMS_MODULE_NUM_STATE_OF_CHARGES):
            if check_voltage_is_valid(self._voltages[i]):
                tick_now = get_tick_count()
                self._EKF_models[i].run_EKF((tick_now - self._tick_last_soc_compute[i]) / pdMS_TO_TICKS(1) / 1000.0, 
                                            self.current,
                                            self.past_voltages[i].get_avg()) # changes units to seconds
                
                local_soc_list[i] = self._EKF_models[i].stateX[0]
                self._tick_last_soc_compute[i] = tick_now
            else:
                # If voltage is invalid, assume bms module is not connected
                local_soc_list[i] = BATTERY_SOC_INITIAL_VALUE

        with self.lock:
            for i in range(BMS_MODULE_NUM_STATE_OF_CHARGES):
                self._state_of_charges[i] = local_soc_list[i]   


class BMS():
    
    def __init__(self, spi_handle : SPI, spi_cs_ports : list[GPIO]):

        self.init_flag = 0
        self._bms_modules : list[BmsModule] = []

        for i in range(BMS_NUM_BMS_MODULES):
            self._bms_modules.append(BmsModule(i, spi_handle, spi_cs_ports[i]))    
        
        self._run_thread_handle = None

        if self._run_thread_handle == None:
            self._run_thread_handle = Worker(target=self.run_thread)
            self._run_thread_handle.start()


    def get_temperature(self, temperatures : list[float], bms_module_id : int, mode : GetMode) -> bool:
        
        if bms_module_id < BMS_NUM_BMS_MODULES:
            self._bms_modules[bms_module_id].get_temperature(temperatures, mode)
            return True
        else:
            return False


    def get_voltage(self, voltages : list[float], bms_module_id : int, mode : GetMode) -> bool:
        
        if bms_module_id < BMS_NUM_BMS_MODULES:
            self._bms_modules[bms_module_id].get_voltage(voltages, mode)
            return True
        else:
            return False

    def get_state_of_charge(self, state_of_charges : list[float], bms_module_id : int) -> bool:
        
        if bms_module_id < BMS_NUM_BMS_MODULES:
            self._bms_modules[bms_module_id].get_state_of_charge(state_of_charges)
            return True
        else:
            return False

    def set_current(self, current : float) -> None:
        
        for bms_module in self._bms_modules:

            if bms_module.init_flag:
                bms_module.current = current


    def measure_with_all_bms_modules(self):
        
        for bms_module in self._bms_modules:

            bms_module.measure_voltage()
            bms_module.measure_temperature()
            bms_module.compute_soc()

    def run_thread(self):
        for i in range(BMS_NUM_BMS_MODULES):
            while not self._bms_modules[i].init_flag:
                pass

        self.init_flag = 1
        i = 0
        while True:
            self.measure_with_all_bms_modules()
            i += 1
        
        



# This is supposed to be a substitute for xTaskTickCount, but no clue if this is correct or if it is even necessary
def get_tick_count():
    return int(time.time() * 1000)

def ticks_to_s(ticks : int) -> float:
    configTICK_RATE_HZ = 1000

    return ticks / configTICK_RATE_HZ

def pdMS_TO_TICKS(xTimeInMs : int) -> int:

    configTICK_RATE_HZ = 1000

    return (xTimeInMs * configTICK_RATE_HZ) / 1000


def check_temperature_is_valid(temperature : float) -> bool:
    return (temperature > BMS_DISCONNECTED_TEMPERATURE_THRESHOLD
            and temperature != BATTERY_TEMPERATURES_INITIAL_VALUE)

def check_voltage_is_valid(voltage : float) -> bool:  

    return (voltage < BMS_DISCONNECTED_VOLTAGE_THRESHOLD 
            and voltage > 1.6 
            and voltage != BATTERY_CELL_VOLTAGES_FAKE_VALUE)




