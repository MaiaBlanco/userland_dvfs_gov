from __future__ import print_function
import time
import cpu_usage
import telnetlib as tel
import atexit
import sys
from random_freq import RandomGovernor

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def getTelnetPower(SP2_tel, last_power):
	# Get the latest data available from the telnet connection 
	# without blocking
	tel_dat = str(SP2_tel.read_very_eager())
	# find latest power measurement in the data
	findex = tel_dat.rfind('\n')
	findex2 = tel_dat[:findex].rfind('\n')
	findex2 = findex2 if findex2 != -1 else 0
	ln = tel_dat[findex2:findex].strip().split(',')
	if len(ln) < 2:
		eprint("ERROR: no power data! Using previous reading.")
		total_power = last_power
	else:
		total_power = float(ln[-1])
	return total_power

# Time to wait between logging a line in s (target, not guaranteed)
DELAY=0.2
# Random governor refresh
REFRESH=30
out_file = None
MAX_SAMPLES = 1000000

header = "time watts w_big w_little w_gpu w_mem usage_c0 usage_c1 usage_c2 usage_c3 usage_c4 usage_c5 usage_c6 usage_c7 temp4 temp5 temp6 temp7 temp_gpu freq_little_cluster freq_big_cluster freq_gpu freq_mem, volts_little_cluster volts_big_cluster volts_gpu volts_mem"
header = "\t".join( header.split(' ') )

def usage():
	eprint("USAGE: {} [output filename]".format(sys.argv[0]))
	sys.exit(1)

def cleanup():
	#cpu_usage.unsetUserSpace()	
	if out_file is not None:
		out_file.close()

if __name__ == "__main__":
	if len(sys.argv) > 2:
		usage()
	if len(sys.argv) == 1:
		out_file = None
		eprint("No logfile given. Outputting to stdout only.")
	else:	
		out_fname = sys.argv[1]#raw_input("Filename for logging: ")
		out_file = open(out_fname, 'w')
		out_file.write(header)
		out_file.write("\n")
		eprint("Outputting to logfile ({}) and to stdout".format(sys.argv[1]))
	atexit.register(cleanup)
	# Set userspace governor:
	#cpu_usage.setUserSpace()
	try:
		SP2_tel = tel.Telnet("192.168.4.1")
		eprint("Getting power measure from SP2.")
		connected = True
	except:
		eprint("Can't connect to smartpower for power logging. Skipping.")
		cont = raw_input("Continue? (y/n)")
		if cont != y:
			eprint("Quitting")
			sys.exit()
		connected = False
	time_stamp = time.time()
	total_power = 0.0
	samples_taken = 0
	gov = RandomGovernor()
	start_time = time.time()
	elapsed_sum = 0
	while True and samples_taken < MAX_SAMPLES:	
		samples_taken += 1
		last_time = time.time()#time_stamp
		temps = cpu_usage.getTemps()
		# Set temperatures for the small, big, gpu and memory. Convert to kelvin
		T = [0.0]*4
		T[0] = sum(temps)/len(temps)+ 273.15
		T[1] = max(temps[0:4]) 	+ 273.15
		T[2] = temps[4] 		+ 273.15
		T[3] = max(temps[0:4]) 	+ 273.15
		usages = cpu_usage.getCpuLoad()	
		F = [0, 0, 0, 0]
		# Get frequency of small cluster, big cluster, GPU, and mem (convert from Khz to hz)
		F[0] = float(cpu_usage.getClusterFreq(0))*1000
		F[1] = float(cpu_usage.getClusterFreq(4))*1000
		F[2] = float(cpu_usage.getGPUFreq())*1000
		F[3] = float(cpu_usage.getMemFreq())*1000
		# Get voltages for each resource (function returns volts so no conversion necessary):
		V = [0.0, 0.0, 0.0, 0.0]
		V[0] = cpu_usage.resVoltage(0)
		V[1] = cpu_usage.resVoltage(4)
		V[2] = cpu_usage.GPUVoltage()
		V[3] = cpu_usage.memVoltage()
		if connected:
			total_power = getTelnetPower(SP2_tel, total_power)
			print(total_power)
		power_comps = cpu_usage.getPowerComponents()

		time_stamp = last_time
		# Data writeout:
# "time watts w_big w_little w_gpu w_mem usage_c0 usage_c1 usage_c2 usage_c3 usage_c4 usage_c5 usage_c6 usage_c7 temp4 temp5 temp6 temp7 temp_gpu freq_little_cluster freq_big_cluster freq_gpu freq_mem, volts_little_cluster volts_big_cluster volts_gpu volts_mem"

		fmt_str = "{}\t"*27
		out_ln = fmt_str.format(\
			time_stamp, total_power, power_comps[0], power_comps[1], power_comps[2], power_comps[3],\
			usages[0], usages[1], usages[2], usages[3], \
			usages[4], usages[5], usages[6], usages[7],\
			temps[0], temps[1], temps[2], temps[3], temps[4], \
			F[0], F[1], F[2], F[3],
			V[0], V[1], V[2], V[3],
			)
		#print(out_ln)
		if not out_file is None:
			out_file.write(out_ln)
			out_file.write("\n")
		elapsed = time.time() - last_time
		elapsed_sum = time.time() - start_time
		if elapsed_sum >= REFRESH:
			start_time = time.time()
			gov.tick()
		time.sleep( max(0, DELAY - elapsed ) )	
