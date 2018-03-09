sudo echo userspace > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
sudo echo userspace > /sys/devices/system/cpu/cpufreq/policy4/scaling_governor

sudo echo 200000 > /sys/devices/system/cpu/cpufreq/policy0/scaling_setspeed

# Blackscholes
for i in 800000 2000000
do 
	sudo echo $i > /sys/devices/system/cpu/cpufreq/policy4/scaling_setspeed
	sleep 120
	# run blackscholes
	time sudo taskset --all-tasks 0xf0 /home/odroid/hw1_files/parsec_files/blackscholes 4 /home/odroid/hw1_files/parsec_files/in_10M_blackscholes.txt /dev/null
	sleep 120;
done

# Bodytrack
for i in 800000 2000000
do 
	sudo echo $i > /sys/devices/system/cpu/cpufreq/policy4/scaling_setspeed
	sleep 120
	# run bodytrack
	time sudo taskset --all-tasks 0xf0 /home/odroid/hw1_files/parsec_files/bodytrack /home/odroid/hw1_files/parsec_files/sequenceB_261 4 260 3000 8 3 4 0
	sleep 120;
done
