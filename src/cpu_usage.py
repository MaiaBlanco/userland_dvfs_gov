import time
import sys, os
import sysfs_paths as sysfs
import atexit 

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
# Interval for sampling CPU load, in seconds
INTERVAL = 0.05

prev_gov_0 = 'ondemand'
prev_gov_1 = 'ondemand'

def getTimeList(n=None):
	"""
	Fetches a list of time units the cpu has spent in various modes
	Detailed explanation at http://www.linuxhowtos.org/System/procstat.htm
	"""
	if n is None:	
		cpuStats = file("/proc/stat", "r").readline().strip()
		columns = cpuStats.replace("cpu", "").split(" ")
		return map(int, filter(None, columns))
	else:
		with open("/proc/stat", "r") as procs:
			# Read out the first line which is aggregate usage
			cpuStats_l = [x for x in procs.read().split('\n') if 'cpu' in x]
			cpuStats_l = [e.strip().split(' ')[1:] for e in cpuStats_l]
			if n == -1:
				columns = cpuStats_l[1:]
				return [map(int, filter(None, cpu_row)) for cpu_row in columns]
			else:
				columns = cpuStats_l[n+1]
				return map(int, filter(None, columns))

def deltaTime(interval, n=None):
	"""
	Returns the difference of the cpu statistics returned by getTimeList
	that occurred in the given time delta
	"""
	timeList1 = getTimeList(n)	
	time.sleep(interval)
	timeList2 = getTimeList(n)
	# -1 returns all cpus:
	if n == -1:
		all_deltas = []
		for i in range(len(timeList1)):
			all_deltas.append(
			[(t2-t1) for t1, t2 in zip(timeList1[i], timeList2[i])]
			)		
		return all_deltas
	else:
		return [(t2-t1) for t1, t2 in zip(timeList1, timeList2)]

def getCpuLoad(n=None, interval=INTERVAL):
	"""
	Returns the cpu load as a value from the interval [0.0, 1.0]
	"""
	dt = deltaTime(interval,n)
	if n > -1:
		idle_time = float(dt[3])
		total_time = sum(dt)
		load = 1-(idle_time/total_time)
		return load
	else:
		idle_times = [float(y[3]) for y in dt]
		total_times = [sum(y) for y in dt]
		loads = [(1-(x/y)) for x,y in zip(idle_times, total_times)]
		return loads

def getAvailFreqs(cpu_num):
	cluster = (cpu_num//4) * 4
	freqs = open(sysfs.fn_cluster_freq_range.format(cluster)).read().strip().split(' ')
	return freqs

def getClusterUsage(cluster_num):
	with open(sysfs.fn_cluster_cpus.format(cluster_num),'r') as affected_cpus:
		cpus = [int(x) for x in affected_cpus.read().strip().strip().split(' ')]
		use = [getCpuLoad(x) for x in cpus]
		#total_load = sum(use)/float(len(use))
		return use #total_load
		
def setUserSpace():
	with open(sysfs.fn_cluster_gov.format(0), 'r') as f:
		prev_gov_0 = f.readline().strip()
	with open(sysfs.fn_cluster_gov.format(4), 'r') as f:
		prev_gov_1 = f.readline().strip()
	with open(sysfs.fn_cluster_gov.format(0), 'w') as f:
		f.write('userspace')
	with open(sysfs.fn_cluster_gov.format(4), 'w') as f:
		f.write('userspace')

def unsetUserSpace():
	with open(sysfs.fn_cluster_gov.format(0), 'w') as f:
		f.write(prev_gov_0)
	with open(sysfs.fn_cluster_gov.format(4), 'w') as f:
		f.write(prev_gov_1)

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
		return int(825000)

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
