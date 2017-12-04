import psutil
import subprocess
import time 
import sys
from timeit import default_timer as timer

TRIALS = 25 

mask = sys.argv[1]#input("Enter cpu mask")
cmd = sys.argv[2]#input("enter command to run")
command = "taskset --all-tasks {} ./{}".format(mask, cmd)

time_count = 0

#start = time.clock()
for i in range(TRIALS):
	start=timer()
	subprocess.call(command.split(), stdout=None)
	time_count += timer() - start
#end = time.clock()
print("Time average over {} runs is {}".format(TRIALS, time_count/TRIALS))

