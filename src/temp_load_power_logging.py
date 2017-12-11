import serial
import time
import cpu_usage
import telnetlib as tel
import atexit
import power_model as pw
import therm_params as tp

# Time to wait between logging a line in ms (target, not guaranteed)
DELAY=0.1
# power used by ethernet and wifiusb when active (assuming they are active)
board_power = 1.71
peripheral_power = 0.072 + 0.472 + board_power
out_file = None

header = "time watts w_leak w_dyn w_periph usage_c0 usage_c1 usage_c2 usage_c3 usage_c4 usage_c5 usage_c6 usage_c7 temp4 temp5 temp6 temp7 temp_gpu freq_little_cluster freq_big_cluster freq_gpu freq_mem volts_little_cluster volts_big_cluster volts_gpu volts_mem"
header = "\t".join( header.split(' ') )

def cleanup():
	#cpu_usage.unsetUserSpace()	
	if out_file is not None:
		out_file.close()

if __name__ == "__main__":
	out_fname = raw_input("Filename for logging: ")
	if len(out_fname) == 0:
		out_file = None
	else:	
		out_file = open(out_fname, 'w')
		out_file.write(header)
		out_file.write("\n")
	atexit.register(cleanup)
	# Set userspace governor:
	#cpu_usage.setUserSpace()
	try:
		SP2_tel = tel.Telnet("192.168.4.1")
		print("Getting power measure from SP2.")
		connected = True
	except:
		print("Can't connect to smartpower for power logging. Skipping.")
		connected = False
	time_stamp = time.time()
	while True:	
		last_time = time.time()#time_stamp
		temps = cpu_usage.getTemps()
		# Set temperatures for the small, big, gpu and memory. Convert to kelvin
		T = [0.0]*4
		T[0] = sum(temps)/len(temps)+ 273.15
		T[1] = max(temps[0:4]) 	+ 273.15
		T[2] = temps[4] 		+ 273.15
		T[3] = max(temps[0:4]) 	+ 273.15
		# -1 indicates get loads for all cpus
		# 0.05 indicates s interval for measurement
		usages = cpu_usage.getCpuLoad(-1, 0.05)	
		F = [0, 0, 0, 0]
		# Get frequency of small cluster, big cluster, GPU, and mem (convert from Khz to hz, except for GPU freq which is already reported by sysfs in hz)
		F[0] = float(cpu_usage.getClusterFreq(0))*1000
		F[1] = float(cpu_usage.getClusterFreq(4))*1000
		F[2] = float(cpu_usage.getGPUFreq())
		F[3] = float(cpu_usage.getMemFreq())*1000
		# Get voltages for each resource (function returns volts so no conversion necessary):
		V = [0.0, 0.0, 0.0, 0.0]
		V[0] = cpu_usage.resVoltage(0)
		V[1] = cpu_usage.resVoltage(4)
		V[2] = cpu_usage.GPUVoltage()
		V[3] = cpu_usage.memVoltage()
		total_power = 0.0
		if connected:
			tel_dat = str(SP2_tel.read_until('\r', timeout=0.11))
			# find latest power measurement in the data
			findex = tel_dat[0:len(tel_dat)].find('\n')
			ln = tel_dat[findex:].strip().split(',')
			#print(ln)
			if len(ln) < 2:
				print("ERROR: len is < 2!")
				total_power = 0
			else:
				total_power = float(ln[-2])
		

		# Now compute the leakage power of each resource
		Pl = [0.0, 0.0, 0.0, 0.0]
		#print("Volts: {}".format(V))
		#print("Hz: {}".format(F))
		#print("Temp: {}".format(T))
		total_leakage_power = 0.0
		Pl[0] = pw.leakagePower(tp.c1, tp.c2, tp.Igate, V[0], T[0])
		Pl[1] = pw.leakagePower(tp.c1, tp.c2, tp.Igate, V[1], T[1])
		Pl[2] = pw.leakagePower(tp.c1, tp.c2, tp.Igate, V[2], T[2])
		Pl[3] = pw.leakagePower(tp.c1, tp.c2, tp.Igate, V[3], T[3])
		total_leakage_power = sum(Pl)
		total_dynamic_power = total_power - total_leakage_power - peripheral_power

	
		time_stamp = last_time
		# Data writeout:
		fmt_str = "{}\t"*26
		out_ln = fmt_str.format(\
			time_stamp, total_power, total_leakage_power, total_dynamic_power, peripheral_power,\
			usages[0], usages[1], usages[2], usages[3], \
			usages[4], usages[5], usages[6], usages[7],\
			temps[0], temps[1], temps[2], temps[3], temps[4], \
			F[0], F[1], F[2], F[3],
			V[0], V[1], V[2], V[3],
			)
		print(out_ln)
		if not out_file is None:
			out_file.write(out_ln)
			out_file.write("\n")
		elapsed = time.time() - last_time
		time.sleep( max(0, DELAY - elapsed ) )	
