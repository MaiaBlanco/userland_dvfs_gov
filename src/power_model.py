# NOTE: Requires telnet connection over wifi to the SmartPower2, which provides power data.
# SP2 is usually at ip 192.168.4.1

import cpu_usage
import psutil
import therm_params as tp
import math
import telnetlib as tel
import time

# leakage power for a given resource (specified by the input model parameters)
def leakagePower(c1, c2, igate, v, t):
	return v*(c1 * math.pow(t, 2) * math.exp(c2/t) + igate)

if __name__=="__main__":
	SP2_tel = tel.Telnet("192.168.4.1")
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
		F = [0, 0, 0, 0]
		# Get frequency of small cluster, big cluster, GPU, and mem (convert from Khz to hz, except for GPU freq which is already reported by sysfs in hz)
		F[0] = float(cpu_usage.getClusterFreq(0))*1000
		F[1] = float(cpu_usage.getClusterFreq(4))*1000
		F[2] = float(cpu_usage.getGPUFreq())
		F[3] = float(cpu_usage.getMemFreq())*1000
		# Get voltages for each resource (function returns volts so no conversion necessary):
		V = [0, 0, 0, 0]
		V[0] = cpu_usage.resVoltage(0)
		V[1] = cpu_usage.resVoltage(4)
		V[2] = cpu_usage.GPUVoltage()
		V[3] = cpu_usage.memVoltage()
		# Now compute the leakage power of each resource
		Pl = [0, 0, 0, 0]
		print("Volts: {}".format(V))
		print("Hz: {}".format(F))
		print("Temp: {}".format(T))
		total_leakage_power = 0.0
		for index in range(4):
			Pl[index] = leakagePower(tp.c1, tp.c2, tp.Igate, V[index], T[index])
			total_leakage_power += Pl[index]
		print("Total leakage_power is {} Watts".format(total_leakage_power))
		tel_dat = str(SP2_tel.read_until('\r', timeout=0.12))
		# find latest power measurement in the data
		findex = tel_dat[0:len(tel_dat)].find('\n')
		ln = tel_dat[findex:].strip().split(',')
		print(ln)
		if len(ln) < 2:
			continue
		total_power = float(ln[-2])
		time.sleep(0.05)
		print("Total power is {} Watts".format(total_power))
		print("Total dynamic power is {} Watts".format(total_power - total_leakage_power))
		
		# estimate activity coefficient (alphaC) based on total activity and current board power

















		# need to estimate leakage power for:
		# big cluster
		# little cluster
		# GPU
		# memory

		# Therefore, need frequency of each of these
		# assume same c1, c2, for big and little clusters and GPU. Might as well assume the same for memory, too...
	
