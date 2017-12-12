import sys
sys.path.append("..")
import cpu_usage as sysfs_utils
import time
import os
import sysfs_paths as sysfs
import math
import atexit

CLUSTER_UP_THRESH = 0.8
LOAD_TARGET = CLUSTER_UP_THRESH
# Sampling rate in steps of microseconds (us)
FREQ_SAMPLING_RATE = 100
CLUSTER_SIZE = 4
REFRESH_PERIOD = 0.1

def usage():
	print("USAGE: {} [cluster,numbers,separated,by,commas]", sys.argv[0])
	sys.exit(1)

def target_frequency(curr_usage, target_usage, current_freq_khz):
	return math.ceil( (curr_usage * current_freq_khz) / (target_usage * 100000) ) * 100000

if __name__ == "__main__":
	clusters = [0,4]
	if len(sys.argv) > 1:
		try:
			clusters = [int(x) for x in sys.argv[1].split(",")]
		except:
			usage()
	print("Starting userspace ondemand.")
	atexit.register(sysfs_utils.unsetUserSpace, clusters=clusters)
	sysfs_utils.setUserSpace(clusters=clusters)
	avail_freqs = [list()] * (sorted(clusters)[-1] + 1)
	sel_cluster_freq = [0] * (sorted(clusters)[-1] + 1)
	for cluster in clusters:
		avail_freqs[cluster] = sysfs_utils.getAvailFreqs(cluster)
	Fs = [[0]] * (sorted(clusters)[-1] + 1)
	Fs_new =  [[0]] * (sorted(clusters)[-1] + 1)
	U = [0.0] * (sorted(clusters)[-1] + 1)
	while True:
		last_time = time.time()
		# Get the latest cpu usages
		cpu_loads = sysfs_utils.getCpuLoad(n=-1, interval=0.05)
		for cluster in clusters:
			if max(cpu_loads[cluster:(cluster+CLUSTER_SIZE)]) > CLUSTER_UP_THRESH:
				# increase the cluster frequency to max
				sel_cluster_freq[cluster] = len(avail_freqs[cluster])-1
				sysfs_utils.setClusterFreq(cluster, \
						avail_freqs[cluster][sel_cluster_freq[cluster]])
			else:
				# find a frequency that will maintain no more than LOAD_TARGET usage on any core.
				Fs[cluster] = sysfs_utils.getClusterFreq(cluster)
				Fs_new[cluster] = target_frequency(max(cpu_loads[cluster:(cluster+CLUSTER_SIZE)]),\
													LOAD_TARGET, Fs[cluster])
				# Search up to and including the current frequency for one that maintains the 
				# desired load:
				for index in range(	sel_cluster_freq[cluster] + 1 ):
					if avail_freqs[cluster][index] >= Fs_new[cluster]:
						sel_cluster_freq[cluster] = index
						sysfs_utils.setClusterFreq(cluster, avail_freqs[cluster][index])
						break
		time.sleep( max(0, REFRESH_PERIOD - ( time.time() - last_time ) ) )
		#print("period {} s".format( time.time() - last_time ) )

					

			
