import sys
sys.path.append("..")
import cpu_usage as sysfs_utils
import time
import os
import sysfs_paths as sysfs

if __name__ == "__main__":
	if len(sys.argv) > 1:
		cluster
	print("Starting userspace ondemand.")
	atexit.register(sysfs_utils.unsetUserSpace)
	sysfs_utils.setUserSpace()
	while True:
		# Get the latest cpu usages
