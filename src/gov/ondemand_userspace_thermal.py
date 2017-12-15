import sys
sys.path.append("..")
import cpu_usage as sysfs_utils
import time
import os
import sysfs_paths as sysfs
import math
import atexit
import psutil

# Thermal threshold in celsius
THERMAL_THRESH = 70
CLUSTER_UP_THRESH = 0.8
LOAD_TARGET = 50
# Sampling rate in steps of microseconds (us)
CLUSTER_SIZE = 4
REFRESH_PERIOD = 0.15
MAX_THERMAL_FREQ_INDEX = 0
# CPU usage polling period MUST be less than or equal to 
# the refresh period. Minimum suggested in psutil docs is 0.1 s
CPU_USAGE_PERIOD = REFRESH_PERIOD - 0.005 

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
	MAX_THERMAL_FREQ_INDEX = len(avail_freqs[cluster])-1
	while True:
		last_time = time.time()
		# Get the latest cpu usages
		#cpu_loads = sysfs_utils.getCpuLoad(n=-1, interval=CPU_USAGE_PERIOD)
		cpu_loads = [ float(x)/100 for x in \
			psutil.cpu_percent(interval=CPU_USAGE_PERIOD, percpu=True)]
		for cluster in clusters:
			if cluster == 4:
				# get the first four temp which correspond to the big cluster cores
				T = sysfs_utils.getTemps()[0:4]
				if max(T) >= THERMAL_THRESH:
					MAX_THERMAL_FREQ_INDEX = max(MAX_THERMAL_FREQ_INDEX - 1, 0)
					#print("Tripped thermal limit. ({} > {})".format(max(T), THERMAL_THRESH))
				else:
					MAX_THERMAL_FREQ_INDEX = len(avail_freqs[cluster])-1
			else:
				MAX_THERMAL_FREQ_INDEX = len(avail_freqs[cluster])-1
			if max(cpu_loads[cluster:(cluster+CLUSTER_SIZE)]) > CLUSTER_UP_THRESH:
				# increase the cluster frequency to max
				sel_cluster_freq[cluster] = MAX_THERMAL_FREQ_INDEX
				#print("Tripped load limit. ({} > {})".format(max(cpu_loads[cluster:(cluster+CLUSTER_SIZE)]), CLUSTER_UP_THRESH))
			else:
				# find a frequency that will maintain no more than LOAD_TARGET usage on any core.
				Fs[cluster] = sysfs_utils.getClusterFreq(cluster)
				Fs_new[cluster] = target_frequency(max(cpu_loads[cluster:(cluster+CLUSTER_SIZE)]),\
													LOAD_TARGET, Fs[cluster])
				# Search up to and including the current frequency for one that maintains the 
				# desired load:
				for index,frequency in enumerate(avail_freqs[cluster]):
					if frequency == Fs_new[cluster]:
						sel_cluster_freq[cluster] = index
						break
					elif frequency > Fs_new[cluster]:
						sel_cluster_freq[cluster] = max(index-1, 0)
						break
					elif index >= MAX_THERMAL_FREQ_INDEX:
						sel_cluster_freq[cluster] = MAX_THERMAL_FREQ_INDEX
						break
			selected_index = sel_cluster_freq[cluster]
			try:
				sysfs_utils.setClusterFreq(cluster, \
											avail_freqs[cluster][selected_index])
			except:
				print("ERROR: tried to access {} for cluster {}".format(selected_index, cluster))
				print(avail_freqs[cluster])
		time.sleep( max(0, REFRESH_PERIOD - ( time.time() - last_time ) ) )
		#print("period {} s".format( time.time() - last_time ) )

					

			
