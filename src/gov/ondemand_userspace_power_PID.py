'''
Modified Ondemand frequency governor with power limit.
When power limit is tripped, reduce frequency aggressively.
Otherwise, engage a proportional model to scale the frequency up
based on the remaining power budget.
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
import telnetlib as tel

from shared_ondemand_params import (
				POWER_THRESH,
				CLUSTER_UP_THRESH,
				LOAD_TARGET,
				CLUSTER_SIZE,
				REFRESH_PERIOD,
				P
				)

from shared_ondemand_params import target_frequency


def usage():
	print("USAGE: {} [options]", sys.argv[0])
	print("Options are:")
	print("-p POWER_LIMIT_WATTS")
	print("-c cluster,numbers,separated,by,commas")
	sys.exit(1)

def getTelnetPower(SP2_tel, last_power):
	# Get the latest data available from the telnet connection 
	# without blocking
	tel_dat = str(SP2_tel.read_eager())
	# find latest power measurement in the data
	findex = tel_dat.rfind('\n')
	findex2 = tel_dat[:findex].rfind('\n')
	findex2 = findex2 if findex2 != -1 else 0
	ln = tel_dat[findex2:findex].strip().split(',')
	if len(ln) < 2:
		print("ERROR: no power data! Using previous reading.")
		total_power = last_power
	else:
		total_power = float(ln[-2])
	return total_power

def setup(clusters, POWER_THRESH):
	SP2_tel = tel.Telnet("192.168.4.1")
	print("Starting userspace ondemand with power limit of {} watts.".format(POWER_THRESH))
	print("Running for clusters: {}".format(clusters))
	print("WARNING: power limit only in effect for the big cluster.")
	atexit.register(sysfs_utils.unsetUserSpace, clusters=clusters)
	sysfs_utils.setUserSpace(clusters=clusters)
	return SP2_tel


def ondemand_power(clusters, POWER_THRESH):
	# Setup output and making sure system is in userspace gov
	SP2_tel = setup(clusters, POWER_THRESH)
	# Setup runtime vars:
	avail_freqs = {x:list() for x in clusters}
	sel_cluster_freq = {x:0 for x in clusters}
	for cluster in clusters:
		avail_freqs[cluster] = sysfs_utils.getAvailFreqs(cluster)
	Fs = {x:0 for x in clusters}
	Fs_new =  {x:0 for x in clusters}
	U = {x:0.0 for x in clusters}
	total_power = 0
	MAX_FREQ_INDICES = {x:0 for x in clusters}
	# Run the governor:
	while True:
		last_time = time.time()
		# Get the latest cpu usages
		cpu_loads = sysfs_utils.getCpuLoad(n=-1, interval=0.0)
		print(cpu_loads)
		for cluster in clusters:
			# Code to handle power limits ********************************************************
			if cluster == 4:
				total_power = getTelnetPower(SP2_tel, total_power)
				remaining_power = POWER_THRESH - total_power
				if remaining_power <= 0:
					MAX_FREQ_INDICES[cluster] = max(MAX_FREQ_INDICES[cluster] - 1, 0)
					print("Tripped power limit. ({} > {})".format(total_power, POWER_THRESH))
				else:
					MAX_FREQ_INDICES[cluster] += math.floor(remaining_power * P)	
					MAX_FREQ_INDICES[cluster] = min( len(avail_freqs[cluster])-1, 
														MAX_FREQ_INDICES[cluster] )
			else: # Else if the little cluster, just proceed as ondemand would normally
				MAX_FREQ_INDICES[cluster] = len(avail_freqs[cluster])-1
			# End code to handle power limits ****************************************************

			# In the case of either cluster, apply the ondemand algorithm, but with upper freq limit
			if max(cpu_loads[cluster:(cluster+CLUSTER_SIZE)]) > CLUSTER_UP_THRESH:
				# increase the cluster frequency to maximum allowed
				sel_cluster_freq[cluster] = MAX_FREQ_INDICES[cluster]
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
					elif index >= MAX_FREQ_INDICES[cluster]:
						sel_cluster_freq[cluster] = MAX_FREQ_INDICES[cluster]
						break
			selected_index = int(sel_cluster_freq[cluster])
			try:
				sysfs_utils.setClusterFreq(cluster, \
											avail_freqs[cluster][selected_index] )
			except:
				print(sys.exc_info()[0])
				print("ERROR: tried to access {} for cluster {}".format(selected_index, cluster))
				print(avail_freqs[cluster])
		time.sleep( max(0, REFRESH_PERIOD - ( time.time() - last_time ) ) )
		#print("period {} s".format( time.time() - last_time ) )

if __name__ == "__main__":
	clusters = [0,4]
	if len(sys.argv) > 1:
		print(sys.argv)
		try:
			try:
				core_index = sys.argv.index('-c')
				clusters = [int(x) for x in sys.argv[core_index+1].split(",")]
			except:
				core_index = -1
			try:
				power_index = sys.argv.index('-p')
			except:
				power_index = -1
			if power_index > -1:
				POWER_THRESH = float(sys.argv[power_index+1])
		except:
			usage()
	ondemand_power(clusters, POWER_THRESH)
