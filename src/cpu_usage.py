import time
import sys, os
import sysfs_paths as sysfs
import atexit
import psutil

# Userspace cpu frequency governor
# Based on:
# https://stackoverflow.com/questions/1296703/getting-system-status-in-python#1296816

# On the exynos 5422, cluster 0 is the low-power (LITTLE) cluster and 
# cluster 1 is the high-power (big) cluster.

#Cluster 0 Up Threshold:
CL0_UP_THRESH = 0.9
# Cluster 0 down threshold:
CL0_DN_THRESH = 0.7
#Cluster 1 Up Threshold:
CL1_UP_THRESH = 0.8
# Cluster 1 Down Threshold:
CL1_DN_THRESH = 0.5
# Sampling rate in steps of microseconds (us)
FREQ_SAMPLING_RATE = 100
# Default interval for sampling CPU load, in seconds
INTERVAL = 0.1

prev_govs = list()
times = None


def getCpuLoad(n=None, interval=INTERVAL):
	"""
	Returns the cpu load as a value from the interval [0.0, 1.0]
	"""
	global times
	if not (interval is None or interval == 0.0):
		old_times = psutil.cpu_times(percpu=True)
		time.sleep(interval)
	else:
		old_times = times
	times = psutil.cpu_times(percpu=True)
	if old_times is None or len(old_times) != len(times):
		if n is None or n == -1:
			return [0.0 for x in times]
		else:
			return 0.0
	else:
		if n is None or n == -1:
			old_and_new = zip(old_times, times)
			idle_delta = [y.idle - x.idle for x,y in old_and_new]
			io_delta =  [y.iowait - x.iowait for x,y in old_and_new]
			total_delta =  [sum(y) - sum(x) for x,y in old_and_new]
			loads = [(1-((x+y)/z)) for x,y,z in zip(idle_delta, io_delta, total_delta)]
			loads = [x if x > 0.001 else 0 for x in loads]
			return loads
		else:
			idle_delta = times[n].idle - old_times[n].idle
			io_delta = times[n].iowait - old_times[n].iowait
			total_delta = sum(times[n]) - sum(old_times[n])
			load = 1-((idle_delta + io_delta)/total_delta)
			return (load if load > 0.001 else 0)
#	loads = [x/100 for x in psutil.cpu_percent(interval=INTERVAL, percpu=True)]
#	if n > -1:
#		return loads[n]
#	else:
#		#total = sum(loads)/(100*len(loads))
#		#loads = [total] + loads
#		return loads

def getAvailFreqs(cpu_num):
	cluster = (cpu_num//4) * 4
	freqs = open(sysfs.fn_cluster_freq_range.format(cluster)).read().strip().split(' ')
	return [int(f.strip()) for f in freqs]

def getClusterUsage(cluster_num):
	with open(sysfs.fn_cluster_cpus.format(cluster_num),'r') as affected_cpus:
		cpus = [int(x) for x in affected_cpus.read().strip().strip().split(' ')]
		use = [getCpuLoad(x) for x in cpus]
		#total_load = sum(use)/float(len(use))
		return use #total_load
		
def setUserSpace(clusters=None):
	global prev_govs
	print("Setting userspace")
	if clusters is None:
		clusters = [0, 4]
	elif type(clusters) is int:
		clusters = [clusters]
	elif type(clusters) is not list:
		print("ERROR: input None, int, or list of ints to set/unset userspace function.")
		sys.exit(1)
	prev_govs = ['powersave'] * (sorted(clusters)[-1] + 1)
	for i in clusters:
		if i != 0 and i != 4:
			print("ERROR: {} is not a valid cluster number! Integers 0 and 4 are valid.".format(i))
			sys.exit(1)
		with open(sysfs.fn_cluster_gov.format(i), 'r') as f:
			prev_govs[i] = f.readline().strip()
		with open(sysfs.fn_cluster_gov.format(i), 'w') as f:
			f.write('userspace')

def unsetUserSpace(clusters=None):
	global prev_govs
	if clusters is None:
		clusters = [0, 4]
	elif type(clusters) is int:
		clusters = [clusters]
	elif type(clusters) is not list:
		print("ERROR: input None, int, or list of ints to set/unset userspace function.")
		sys.exit(1)
	for i in clusters:
		if i != 0 and i != 4:
			print("ERROR: {} is not a valid cluster number! Integers 0 and 4 are valid.".format(i))
			sys.exit(1)
		with open(sysfs.fn_cluster_gov.format(i), 'w') as f:
			f.write(prev_govs[i])
	

def getClusterFreq(cluster_num):
	with open(sysfs.fn_cluster_freq_read.format(cluster_num), 'r') as f:
		return int(f.read().strip())
	
# Accepts frequency in khz as int or string
def setClusterFreq(cluster_num, frequency):
	with open(sysfs.fn_cluster_freq_set.format(cluster_num), 'w') as f:
		# todo: add bounds checking
		f.write(str(frequency))	

def getGPUFreq():
	with open(sysfs.gpu_freq, 'r') as f:
		return int(f.read().strip()) 

def getMemFreq():
		# See also in sysfs_paths.py: Linux kernel 4.9 sets mem to const freq (khz)
		return int(750000)

def getTemps():
	templ = []
	for i in range(5):
		temp = float(file(sysfs.fn_thermal_sensor.format(i),'r').readline().strip())/1000
		templ.append(temp)
	# Note: on the 5422, cpu temperatures 5 and 7 (big cores 1 and 3, counting from 0)
	# appear to be swapped.
	# therefore, swap them back:
	t1 = templ[1]
	templ[1] = templ[3]
	templ[3] = t1
	return templ

def lAvg(l):
	return float(sum(l))/len(l)

def resVoltage(n):
	# 0 is little cluster
	# 4 is big cluster
	# TODO: add support for GPU and mem voltages.
	if n == 0:
		temp = float(file(sysfs.little_micro_volts, 'r').readline().strip())/1000000
	elif n == 4:
		temp = float(file(sysfs.big_micro_volts, 'r').readline().strip())/1000000
	else:
		raise Exception('Error: {} is not a supported resource ID for voltage.'.format(n))
	return temp

def GPUVoltage():
	return float(file(sysfs.gpu_micro_volts, 'r').readline().strip())/1000000

def memVoltage():
	return float(file(sysfs.mem_micro_volts, 'r').readline().strip())/1000000

if __name__ == "__main__":
	print("Starting userspace cpu frequency governor. Make sure gov is set to userspace!!.")
	atexit.register(unsetUserSpace)
	setUserSpace()
	while True:
		#print "CPU usage=%.2f%%" % (getCpuLoad()*100.0)
		#for i in range(8):
		#	print "CPU {} usage:{}".format(i, getCpuLoad(i)*100.0)
		# Get per-core cpu util by cluster
		cl0 = getClusterUsage(0)
		freq0 = getClusterFreq(0)
		new_freq0 = freq0
		if max(cl0) > CL0_UP_THRESH:
			# increase the frequency
			new_freq0 =  min(1400000, freq0+int(freq0*0.5))
			setClusterFreq(0, new_freq0)
		elif max(cl0) < CL0_DN_THRESH:
			new_freq0 = max(400000, freq0-int(freq0*0.2))
			setClusterFreq(0, new_freq0)
		cl1 = getClusterUsage(4)
		freq1 = getClusterFreq(4)
		new_freq1 = freq1
		if max(cl1) > CL1_UP_THRESH:
			# increase the frequency
			new_freq1 = min(2000000, freq1+int(freq1*0.7))
			setClusterFreq(4, new_freq1)
		elif max(cl1) < CL1_DN_THRESH:
			new_freq1 = max(20000, freq1-int(freq1*0.2))
			setClusterFreq(4, new_freq1)

		print('cluster\t\told_freq\tnew_freq\ttotal_%\tmax_core_%')
		print('low_power\t{}\t\t{}\t\t{:.1%}\t{:.1%}'.format(freq0, new_freq0, float(sum(cl0))/len(cl0), max(cl0)))
		print('high_power\t{}\t\t{}\t\t{:.1%}\t{:.1%}'.format(freq1, new_freq1, float(sum(cl1))/len(cl1), max(cl1)))
		# todo: use exponential averages over time
		# todo: take temperature ceiling into account
		# todo: refactor to improve performance/overhead	
		#print "Available freqs:\n"
		#print getAvailFreqs(0)
		#print getAvailFreqs(4)
		time.sleep(0.5)
