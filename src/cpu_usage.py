import time
import sys, os

# Based on:
# https://stackoverflow.com/questions/1296703/getting-system-status-in-python#1296816

INTERVAL = 0.1
def getTimeList():
	"""
	Fetches a list of time units the cpu has spent in various modes
	Detailed explanation at http://www.linuxhowtos.org/System/procstat.htm
	"""
	cpuStats = file("/proc/stat", "r").readline()
	columns = cpuStats.replace("cpu", "").split(" ")
	return map(int, filter(None, columns))

def deltaTime(interval):
	"""
	Returns the difference of the cpu statistics returned by getTimeList
	that occurred in the given time delta
	"""
	timeList1 = getTimeList()	
	time.sleep(interval)
	timeList2 = getTimeList()
	return [(t2-t1) for t1, t2 in zip(timeList1, timeList2)]

def getCpuLoad():
	"""
	Returns the cpu load as a value from the interval [0.0, 1.0]
	"""
	dt = list(deltaTime(INTERVAL))
	idle_time = float(dt[3])
	total_time = sum(dt)
	load = 1-(idle_time/total_time)
	return load

def getAvailFreqs(cpu_num):
	cluster = (cpu_num//4) * 4
	freqs = open('/sys/devices/system/cpu/cpufreq/policy{}/scaling_available_frequencies'.format(cluster)).read().split(' ')
	return freqs

while True:
	print "CPU usage=%.2f%%" % (getCpuLoad()*100.0)
	print "Available freqs:\n"
	print getAvailFreqs(0)
	print getAvailFreqs(4)
	time.sleep(0.1)
