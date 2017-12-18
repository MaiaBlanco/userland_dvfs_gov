'''
Author: Mark Blanco
Copyright: Carnegie Mellon University
Date: Dec 2017
'''
import sys
sys.path.append("..")
import cpu_usage as sysfs_utils
import time
import os
import sysfs_paths as sysfs
import math
import atexit
import psutil

from shared_ondemand_params import (
				CLUSTER_UP_THRESH,
				LOAD_TARGET,
				CLUSTER_SIZE,
				REFRESH_PERIOD,
				MAX_THERMAL_FREQ_INDEX,
				)

from shared_ondemand_params import target_frequency

def usage():
	print("USAGE: {} cluster,numbers,separated,by,commas", sys.argv[0])
	sys.exit(1)

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
	avail_freqs = {x:list() for x in clusters}
	sel_cluster_freq = {x:0 for x in clusters}
	for cluster in clusters:
		avail_freqs[cluster] = sysfs_utils.getAvailFreqs(cluster)
	Fs = {x:0 for x in clusters}
	Fs_new =  {x:0 for x in clusters}
	U = {x:0.0 for x in clusters}
	while True:
		last_time = time.time()
		# Get the latest cpu usages
		cpu_loads = sysfs_utils.getCpuLoad(n=-1, interval=0.0)
		for cluster in clusters:
			if max(cpu_loads[cluster:(cluster+CLUSTER_SIZE)]) > CLUSTER_UP_THRESH:
				# increase the cluster frequency to max
				sel_cluster_freq[cluster] = len(avail_freqs[cluster])-1
			else:
				# find a frequency that will maintain no more than LOAD_TARGET usage on any core.
				Fs[cluster] = sysfs_utils.getClusterFreq(cluster)
				Fs_new[cluster] = min( Fs[cluster], target_frequency(max(cpu_loads[cluster:(cluster+CLUSTER_SIZE)]),\
													avail_freqs[cluster][0], avail_freqs[cluster][-1]) )
				# Search up to and including the current frequency for one that maintains the 
				# desired load:
				for index,frequency in enumerate(avail_freqs[cluster]):
					if frequency == Fs_new[cluster]:
						sel_cluster_freq[cluster] = index
						break
					elif frequency > Fs_new[cluster]:
						sel_cluster_freq[cluster] = max(index-1, 0)
						break
			sysfs_utils.setClusterFreq(cluster, \
										avail_freqs[cluster][sel_cluster_freq[cluster]])
		time.sleep( max(0, REFRESH_PERIOD - ( time.time() - last_time ) ) )
		#print("period {} s".format( time.time() - last_time ) )

					

			
