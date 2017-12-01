# NOTE: Requires telnet connection over wifi to the SmartPower2, which provides power data.
# SP2 is usually at ip 192.168.4.1

import cpu_usage
import psutil
import thermal_params as tp
import math
import telnetlib as tel

# leakage power for a given resource (specified by the input model parameters)
def leakagePower(c1, c2, igate, v, t):
	return v*(c1 * math.exp(t, 2) * math.exp(e, (c2/t)) + igate)

if __name__=="__main__":
	SP2_tel = tel.Telnet("192.168.4.1")
	while True:
		print(SP2_tel.read_some())
	# IF RUNNING AS MAIN SCRIPT, EXPECT INPUT FILE WITH RECORDED DATA FOR 
	# VOLTAGE, CURRENT, WATTS, BF, LF
	while(True):
		# getTemps returns core 4, 5, 6, 7 and gpu temperature as floats in celcius
		t = cpu_usage.getTemps()
		# Set temperatures for each (small, big, gpu, mem) (big cluster and GPU are exact; small and mem are approx)
		# mem die is on top of big core, so they should have approx the same max temp
		# small core takes average of all temps.
		T = [0, 0, 0, 0]
		# Set temperatures for the small, big, gpu and memory. Convert to kelvin
		T[0] = sum(t)/len(t)+ 273.15
		T[1] = max(t[0:4]) 	+ 273.15
		T[2] = t[4] 		+ 273.15
		T[3] = max(t[0:4]) 	+ 273.15
		F = [0, 0, 0, 0] 	+ 273.15
		# Get frequency of small cluster, big cluster, GPU, and mem (convert from Khz to hz)
		F[0] = float(cpu_usage.getClusterFreq(0))/1000
		F[1] = float(cpu_usage.getClusterFreq(4))/1000
		F[2] = float(cpu_usage.getGPUFreq())/1000
		F[3] = float(cpu_usage.getMemFreq())/1000
		# Get voltages for each resource (function returns volts so no conversion necessary):
		V = [0, 0, 0, 0]
		V[0] = cpu_usage.resVoltage(0)
		V[1] = cpu_usage.resVoltage(4)
		v[2] = cpu_usage.GPUVoltage()
		v[3] = cpu_usage.memVoltage()
		# Now compute the leakage power of each resource
		Pl = [0, 0, 0, 0]
		total_leakage_power = 0.0
		for index in range(4):
			Pl[index] = leakagePower(tp.c1, tp.c2, tp.Igate, V[index], T[index])
			total_leakage_power += Pl[index]
		print("Total leakage_power is {}".format(total_leakage_power))
		print("Total power is {}".format())
		print("Total dynamic power is {}".format())

		# estimate activity coefficient (alphaC) based on total activity and current board power

















		# need to estimate leakage power for:
		# big cluster
		# little cluster
		# GPU
		# memory

		# Therefore, need frequency of each of these
		# assume same c1, c2, for big and little clusters and GPU. Might as well assume the same for memory, too...
	