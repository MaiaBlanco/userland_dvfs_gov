import time
import sys, os
import sysfs_paths as sysfs
import atexit 
import cpu_usage

atexit.register(cpu_usage.unsetUserSpace)
cpu_usage.setUserSpace()

big_freqs =  cpu_usage.getAvailFreqs(4)
little_freqs = cpu_usage.getAvailFreqs(0)

print(big_freqs)
print(little_freqs)

cpu_usage.setClusterFreq(0, little_freqs[0])
cpu_usage.setClusterFreq(4, big_freqs[0])
bi = 0
li = 0
up = True
while True:
	b_freq = cpu_usage.getClusterFreq(4) 
	l_freq = cpu_usage.getClusterFreq(0)
	b_vdd = cpu_usage.resVoltage(4) 
	l_vdd = cpu_usage.resVoltage(0)
	print("{} {} {} {}".format(l_vdd, l_freq, b_vdd, b_freq))
	if up and li != len(little_freqs)-1:
		li += 1
	elif up and bi != len(big_freqs)-1:
		bi += 1
	elif up and bi == len(big_freqs) - 1:
		up = False
		li -= 1
	elif not up and li > 0:
		li -= 1
	elif not up and bi > 0:
		bi -= 1
	else:
		break
	cpu_usage.setClusterFreq(0, little_freqs[li])
	cpu_usage.setClusterFreq(4, big_freqs[bi])
	time.sleep(0.1)

