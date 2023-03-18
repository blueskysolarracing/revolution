#!/usr/bin/env python
# coding: utf-8

# In[ ]:


pip install pykalman


# In[ ]:


import numpy as np
import pandas as pd
from pykalman import KalmanFilter


# # Defining our battery model

# In[ ]:


def battery_model(x, u):
    # State model function
    # x: state vector [SOC, voltage]
    # u: input vector [current, time]
    R = 0.1 # internal resistance
    Q = 100 # battery capacity
    SOC = x[0]
    V = x[1]
    I = u[0]
    dt = u[1]
    V_oc = 4.1 # open-circuit voltage
    V_est = V_oc - R * I # estimated voltage
    SOC_new = SOC - I * dt / Q # estimated SOC
    x_new = np.array([SOC_new, V_est])
    return x_new

def battery_meas(x):
    # Measurement function
    # x: state vector [SOC, voltage]
    V = x[1]
    return V


# # Need a csv file to interpret the data and get I & V

# In[ ]:


data = pd.read_csv('solar_charging_data.csv')
time = data['Time'].values
current = data['Current'].values
voltage = data['Voltage'].values


# # Creating EKF with the battery model and variations

# In[ ]:


# Initial state estimate
x0 = np.array([0.5, 4.0])

# Initial covariance estimate
P0 = np.eye(2)

# Process noise covariance matrix
Q = np.diag([0.01, 0.01])

# Measurement noise variance
R = 0.1

# Create EKF
ekf = KalmanFilter(
    transition_functions=battery_model,
    observation_functions=battery_meas,
    initial_state_mean=x0,
    initial_state_covariance=P0,
    transition_covariance=Q,
    observation_covariance=R
)


# # Looking through time to get the estimated SOC and Voltage

# In[ ]:


# Initialize arrays to store estimated SOC and voltage
soc_est = np.zeros(len(time))
voltage_est = np.zeros(len(time))

# Initialize state estimate with initial value
x_est = x0

# Loop through each time step
for i in range(len(time)):
    # Define input vector [current, time]
    u = np.array([current[i], time[i]])

    # Predict next state
    x_pred, P_pred = ekf.predict(x_est, P0)

    # Update state estimate using measurement [voltage]
    z = voltage[i]
    x_est, P_est = ekf.update(x_pred, P_pred, z)

    # Store estimated SOC and voltage
    soc_est[i] = x_est[0]
    voltage_est[i] = x_est[1]

    # Update initial state and covariance estimates for next iteration
    x0 = x_est
    P0 = P_est


# # Plotting the SOC

# In[ ]:


import matplotlib.pyplot as plt

plt.figure()
plt.plot(time, soc_est, label='Estimated SOC')
plt.xlabel('Time (s)')
plt.ylabel('SOC')
plt.legend()

plt.figure()
plt.plot(time, voltage, label='Measured voltage')
plt.plot(time, voltage_est, label='

