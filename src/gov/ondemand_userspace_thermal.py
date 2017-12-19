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
				THERMAL_THRESH,
				CLUSTER_UP_THRESH,
				LOAD_TARGET,
				CLUSTER_SIZE,
				REFRESH_PERIOD,
				Pt,
				It
				)

from shared_ondemand_params import target_frequency

def usage():
	print("USAGE: {} [options]", sys.argv[0])
	print("Options are:")
	print("-t THERMAL_LIMIT_CELSIUS")
	print("-c cluster,numbers,separated,by,commas")
	sys.exit(1)

if __name__ == "__main__":
	clusters = [4]
	if len(sys.argv) > 1:
		try:
			try:
				core_index = sys.argv.index('-c')
			except:
				core_index = -1
			if core_index > -1:
				clusters = [int(x) for x in sys.argv[core_index+1].split(",")]
			try:
				therm_index = sys.argv.index('-t')
			except:
				therm_index = -1
			if therm_index > -1:
				THERMAL_THRESH = float(sys.argv[therm_index+1])
		except:
			usage()
	print("Starting userspace ondemand with thermal limit of {} celsius on clusters {}.".format(
										THERMAL_THRESH, clusters))
	print("WARNING: thermal limits are only in effect for the big cluster.")
	atexit.register(sysfs_utils.unsetUserSpace, clusters=clusters)
	sysfs_utils.setUserSpace(clusters=clusters)
	avail_freqs = {x:list() for x in clusters}
	sel_cluster_freq = {x:0 for x in clusters}
	for cluster in clusters:
		avail_freqs[cluster] = sysfs_utils.getAvailFreqs(cluster)
	Fs = {x:0 for x in clusters}
	Fs_new =  {x:0 for x in clusters}
	U = {x:0.0 for x in clusters}
	MAX_THERMAL_FREQ_INDICES = {x:0 for x in clusters}
	headroom_i = 0
	while True:
		last_time = time.time()
		# Get the latest cpu usages
		cpu_loads = sysfs_utils.getCpuLoad(n=-1, interval=0.0)
		for cluster in clusters:
			if cluster == 4:
				# get the first four temp which correspond to the big cluster cores
				T = sysfs_utils.getTemps()[0:4]
				headroom = THERMAL_THRESH - max(T)
				if headroom <= 0:
					MAX_THERMAL_FREQ_INDICES[cluster] = max(MAX_THERMAL_FREQ_INDICES[cluster] - 1, 0)
					print("Tripped thermal limit. ({} > {})".format(max(T), THERMAL_THRESH))
					headroom_i = 0
				else:
					MAX_THERMAL_FREQ_INDICES[cluster] += math.floor(headroom*Pt + headroom_i * It)
					MAX_THERMAL_FREQ_INDICES[cluster] = min(len(avail_freqs[cluster])-1, 
															MAX_THERMAL_FREQ_INDICES[cluster])
					headroom_i += headroom
			else:
				MAX_THERMAL_FREQ_INDICES[cluster] = len(avail_freqs[cluster])-1
			if max(cpu_loads[cluster:(cluster+CLUSTER_SIZE)]) > CLUSTER_UP_THRESH:
				# increase the cluster frequency to max
				sel_cluster_freq[cluster] = MAX_THERMAL_FREQ_INDICES[cluster]
				#print("Tripped load limit. ({} > {})".format(max(cpu_loads[cluster:(cluster+CLUSTER_SIZE)]), CLUSTER_UP_THRESH))
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
					elif index >= MAX_THERMAL_FREQ_INDICES[cluster]:
						sel_cluster_freq[cluster] = MAX_THERMAL_FREQ_INDICES[cluster]
						break
			selected_index = int(sel_cluster_freq[cluster])
			try:
				sysfs_utils.setClusterFreq(cluster, \
											avail_freqs[cluster][selected_index])
			except:
				print("ERROR: tried to access {} for cluster {}".format(selected_index, cluster))
				print(avail_freqs[cluster])
		time.sleep( max(0, REFRESH_PERIOD - ( time.time() - last_time ) ) )
		#print("period {} s".format( time.time() - last_time ) )

					

			
