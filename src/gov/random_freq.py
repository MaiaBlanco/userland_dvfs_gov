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
import random

REFRESH_PERIOD = 30

def usage():
	print("USAGE: {} cluster,numbers,separated,by,commas", sys.argv[0])
	sys.exit(1)

if __name__ == "__main__":
	random.seed()
	clusters = [0,4]
	if len(sys.argv) > 1:
		try:
			clusters = [int(x) for x in sys.argv[1].split(",")]
		except:
			usage()
	print("Starting random frequency governor.")
	atexit.register(sysfs_utils.unsetUserSpace, clusters=clusters)
	sysfs_utils.setUserSpace(clusters=clusters)
	avail_freqs = {x:list() for x in clusters}
	sel_cluster_freq = {x:0 for x in clusters}
	for cluster in clusters:
		avail_freqs[cluster] = sysfs_utils.getAvailFreqs(cluster)
	while True:
		last_time = time.time()
		for cluster in clusters:
			sel_cluster_freq[cluster] = random.randint(0, len(avail_freqs[cluster])-1 )
			sysfs_utils.setClusterFreq(cluster, \
										avail_freqs[cluster][sel_cluster_freq[cluster]])
		time.sleep(random.randint(0, REFRESH_PERIOD))

