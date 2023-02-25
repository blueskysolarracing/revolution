#!/usr/bin/env python
# coding: utf-8

# # Print matrix

# In[ ]:


#for getting a list
from typing import List
#if and end if statement
import sys

if sys.platform.startswith('win'):
    def printMatrix(input: List[float], size: List[int]) -> None:
        for i in range(size[0]):
            for j in range(size[1]):
                print(f"{input[i*size[1] + j]:.8f}  ", end="")
            print()


# # Float SOC

# In[ ]:


def SOC(ocv: float) -> float:
    dsoc: float = 0.0
    docv: float = 0.0
    soc: float = 0.0
    # using method of linear interpolation
    if ocv <= BSSR_OCV[0]:
        soc = 0
        return soc
    elif ocv >= BSSR_OCV[LUT_SIZE-1]:
        soc = 1
        return soc
    elif (ocv > BSSR_OCV[0]) and (ocv < BSSR_OCV[LUT_SIZE-1]):
        # binary search
        lowerIndex: int = 0
        low: int = 0
        high: int = LUT_SIZE-1
        mid: int = 0
        while low <= high:
            mid = (low + high) // 2
            if (ocv >= BSSR_OCV[mid]) and (ocv < BSSR_OCV[mid+1]):
                lowerIndex = mid
                break
            elif ocv < BSSR_OCV[mid]:
                high = mid - 1
            else:
                low = mid + 1
        dsoc = BSSR_SOC[lowerIndex+1] - BSSR_SOC[lowerIndex]
        docv = BSSR_OCV[lowerIndex+1] - BSSR_OCV[lowerIndex]
        soc = (ocv - BSSR_OCV[lowerIndex]) * (dsoc / docv) + BSSR_SOC[lowerIndex]
        return soc
    else:
        print('soc not found')
        return 0.0


# # initBatteryAlgo

# In[ ]:


#no need for list for EKF_battery as it is a struct and python automatically allocates and deallocates the memory
def initBatteryAlgo(inBatteryPack: EKF_Battery, initial_v: List[float], initial_deltaT: float) -> None:
    for unit in range(NUM_14P_UNITS):
        initEKFModel(inBatteryPack.batteryPack[unit], initial_v[unit])

    compute_A_B_dt(initial_deltaT)
    


# # initEKFModel

# In[ ]:


#no need for unsigned integer as python doesnt need to specify specifically
from typing import List

def initEKFModel(inBattery: EKF_Model_14p, initial_v: float) -> None:
    # initialize state variables
    for i in range(STATE_NUM):
        if i == 0:
            inBattery.stateX[i] = SOC(initial_v)
        else:
            inBattery.stateX[i] = 0.0
    
    # initialize the covariance matrix
    for i in range(STATE_NUM):
        for j in range(STATE_NUM):
            if i == j:
                inBattery.covP[i*STATE_NUM + j] = covList[i]
            else:
                inBattery.covP[i*STATE_NUM + j] = 0.0


# # init_A_Matrix

# In[ ]:


#dont know what A is and dim1 is and DELTA_T, R_CT, C_CT, R_D, C_D is

def init_A_Matrix() -> None:
    A[0] = 1.0
    A[4] = math.exp(-DELTA_T/(R_CT*C_CT))
    A[8] = math.exp(-DELTA_T/(R_D*C_D))

    # Debug prints
    if DEBUG_PRINTS:
        print("A initial")
        printMatrix(A, dim1)
        print("\n")


# # init_B_Matrix

# In[ ]:


#unknown variables used

def init_B_Matrix() -> None:
    B[0] = -COULOMB_ETA * DELTA_T / Q_CAP  # in example, this equation is only multiplied by ETA when the current is negative
    B[2] = 1 - exp(-DELTA_T/(R_CT*C_CT))
    B[4] = 1 - exp(-DELTA_T/(R_D*C_D))

    # Debug prints
    if DEBUG_PRINTS:
        print("B initial")
        printMatrix(B, [2, 3])
        print()


# # compute_A_B_dt

# In[ ]:


import math

def compute_A_B_dt(dt: float) -> None:
    A[0] = 1.0
    A[4] = math.exp(-dt/(R_CT*C_CT))
    A[8] = math.exp(-dt/(R_D*C_D))

    B[0] = -COULOMB_ETA*dt/Q_CAP # in example, this equation is only multiplied by ETA when the current is negative
    B[2] = 1 - math.exp(-dt/(R_CT*C_CT))
    B[4] = 1 - math.exp(-dt/(R_D*C_D))
    
    return


# # addition EKF

# In[ ]:


import numpy as np
from typing import List

def addition_EKF(operand_1: List[float], operand_2: List[float], result: List[float], size: List[int], subtract: bool) -> None:

    # check if we are doing addition or subtraction based on the 'subtract' boolean
    # if subtract = 0 then it is addition
    # if subtract = 1 then it is subraction
    coefficient = 1.0 if subtract == False else -1.0

    rows = size[0]
    cols = size[1]

    for i in range(rows):
        for j in range(cols):
            result[i*cols + j] = operand_1[i*cols + j] + coefficient*operand_2[i*cols + j]

    return

