import time
import sys, os
import sysfs_paths as sysfs
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
INTERVAL = 0.1
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
			cpuStats_l = procs.read().split('\n')
			cpuStats_l = [e.strip().split(' ')[1:] for e in cpuStats_l]
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
	return [(t2-t1) for t1, t2 in zip(timeList1, timeList2)]

def getCpuLoad(n=None):
	"""
	Returns the cpu load as a value from the interval [0.0, 1.0]
	"""
	dt = list(deltaTime(INTERVAL,n))
	idle_time = float(dt[3])
	total_time = sum(dt)
	load = 1-(idle_time/total_time)
	return load

def getAvailFreqs(cpu_num):
	cluster = (cpu_num//4) * 4
	freqs = open('/sys/devices/system/cpu/cpufreq/policy{}/scaling_available_frequencies'.format(cluster)).read().split(' ')
	return freqs

def getClusterUsage(cluster_num):
	with open(sysfs.fn_core_cpus,'r') as affected_cpus:
		cpus = affected_cpus.read().split()
		

#def setClusterFreq(cluster_num):

if __name__ == "__main__":
	while True:
		print "CPU usage=%.2f%%" % (getCpuLoad()*100.0)
		for i in range(8):
			print "CPU {} usage:{}".format(i, getCpuLoad(i)*100.0)
		#print "Available freqs:\n"
		#print getAvailFreqs(0)
		#print getAvailFreqs(4)
		time.sleep(0.1)
