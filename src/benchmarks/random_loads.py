import subprocess
import psutil
import random
import time
import os

FNULL = open(os.devnull, 'w')

bench_thresh = 0.1#0.5
period_max = 1#60
bench_processes = []
other_processes = []
input_size = ["native", "simlarge", "simsmall"]
path = "/home/odroid/PARSEC/parsec-3.0/bin/parsecmgmt"
cmd = path + " -a run -p bodytrack -i {} -n {} -c gcc-openmp -s 'sudo taskset --all-tasks {}'"

random.seed()
while True:
	for i in range(len(bench_processes)-1, -1, -1):
		if bench_processes[i].poll() is not None:
			del bench_processes[i]
	# Roll a die:
	d = random.random()
	if d >= bench_thresh and len(bench_processes) == 0:
		print("hi")
		# launch a new benchmark
		affinity_l = random.randint(1, 15)
		affinity_b = random.randint(1, 15)
		affinity = affinity_l | (affinity_b << 4)
		affinity_string = hex(affinity)
		input_s = input_size[random.randint(0, len(input_size)-1)]
		num_threads = random.randint(1, bin(affinity).count("1"))
		cmd_f = cmd.format(input_s, num_threads, affinity_string)
		print(cmd_f)
		bench_processes.append(subprocess.Popen(['/bin/sh', "./parsec.sh", input_s, str(num_threads), affinity_string], stdout=FNULL ))


	time.sleep(random.randint(0, period_max))

