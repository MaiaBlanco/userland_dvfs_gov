'''
Author: Mark Blanco
Copyright: Carnegie Mellon University
Date: Dec 2017
'''

# Function to find next target frequency when downscaling
def target_frequency(curr_usage, min_freq_khz, max_freq_khz):
	return min_freq_khz + (max_freq_khz - min_freq_khz) * curr_usage


# Common configurable paramters for ondemand
CLUSTER_UP_THRESH = 0.90
LOAD_TARGET = CLUSTER_UP_THRESH
REFRESH_PERIOD = 0.25

# Power threshold in watts for power ondemand
POWER_THRESH = 7
# Proportional term for ondemand power regulator
P = 0.7

# Thermal threshold in celsius for thermal ondemand
THERMAL_THRESH = 60
# Proportional term for ondemand thermal regulator
Pt = 0.1
It = 0.1

# Non-configurable params for ondemand
MAX_THERMAL_FREQ_INDEX = 0
CLUSTER_SIZE = 4
