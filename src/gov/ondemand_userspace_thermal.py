import sys
sys.path.append("..")
import cpu_usage as sysfs_utils
import time
import os
import sysfs_paths as sysfs
import math
import atexit

# Thermal threshold in celsius
THERMAL_THRESH = 70
CLUSTER_UP_THRESH = 0.8
LOAD_TARGET = CLUSTER_UP_THRESH
# Sampling rate in steps of microseconds (us)
FREQ_SAMPLING_RATE = 100
CLUSTER_SIZE = 4
REFRESH_PERIOD = 0.1
MAX_THERMAL_FREQ_INDEX = 0

def usage():
	print("USAGE: {} [options]", sys.argv[0])
	print("Options are:")
	print("-t THERMAL_LIMIT_CELCIUS")
	print("-c cluster,numbers,separated,by,commas")
	sys.exit(1)

def target_frequency(curr_usage, target_usage, current_freq_khz):
	return math.ceil( (curr_usage * current_freq_khz) / (target_usage * 100000) ) * 100000

if __name__ == "__main__":
	clusters = [0,4]
	if len(sys.argv) > 1:
		try:
			try:
				core_index = argv.index('-c')
			except:
				core_index = -1
			if core_index > -1:
				clusters = [int(x) for x in sys.argv[core_index+1].split(",")]
			try:
				therm_index = argv.index('-t')
			except:
				therm_index = -1
			if therm_index > -1:
				THERMAL_THRESH = float(sys.argv[therm_index+1])
		except:
			usage()
	print("Starting userspace ondemand with thermal limit of {} celsius.".format(THERMAL_THRESH))
	print("WRNING: thermal limits are only in effect for the big cluster.")
	atexit.register(sysfs_utils.unsetUserSpace, clusters=clusters)
	sysfs_utils.setUserSpace(clusters=clusters)
	avail_freqs = [list()] * (sorted(clusters)[-1] + 1)
	sel_cluster_freq = [0] * (sorted(clusters)[-1] + 1)
	for cluster in clusters:
		avail_freqs[cluster] = sysfs_utils.getAvailFreqs(cluster)
	Fs = [[0]] * (sorted(clusters)[-1] + 1)
	Fs_new =  [[0]] * (sorted(clusters)[-1] + 1)
	U = [0.0] * (sorted(clusters)[-1] + 1)
	MAX_THERMAL_FREQ_INDEX = len(avail_freqs[cluster])-1
	while True:
		last_time = time.time()
		# Get the latest cpu usages
		cpu_loads = sysfs_utils.getCpuLoad(n=-1, interval=0.05)
		for cluster in clusters:
			if cluster == 4:
				# get the first four temp which correspond to the big cluster cores
				T = sysfs_utils.getTemps()[0:4]
				if max(T) >= THERMAL_THRESH:
					MAX_THERMAL_FREQ_INDEX = max(MAX_THERMAL_FREQ_INDEX - 1, 0)
				else:
					MAX_THERMAL_FREQ_INDEX = len(avail_freqs[cluster])-1
			if max(cpu_loads[cluster:(cluster+CLUSTER_SIZE)]) > CLUSTER_UP_THRESH:
				# increase the cluster frequency to max
				sel_cluster_freq[cluster] = MAX_THERMAL_FREQ_INDEX
			else:
				# find a frequency that will maintain no more than LOAD_TARGET usage on any core.
				Fs[cluster] = sysfs_utils.getClusterFreq(cluster)
				Fs_new[cluster] = target_frequency(max(cpu_loads[cluster:(cluster+CLUSTER_SIZE)]),\
													LOAD_TARGET, Fs[cluster])
				# Search up to and including the current frequency for one that maintains the 
				# desired load:
				for index in range(	len(avail_freqs[cluster]) ):
					if avail_freqs[cluster][index] >= Fs_new[cluster]:
						sel_cluster_freq[cluster] = min(index, MAX_THERMAL_FREQ_INDEX)
						break
			sysfs_utils.setClusterFreq(cluster, \
				avail_freqs[cluster][sel_cluster_freq[cluster]])
		time.sleep( max(0, REFRESH_PERIOD - ( time.time() - last_time ) ) )
		#print("period {} s".format( time.time() - last_time ) )

					

			
