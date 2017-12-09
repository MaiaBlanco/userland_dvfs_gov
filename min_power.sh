echo "powersave" > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
echo "powersave" > /sys/devices/system/cpu/cpufreq/policy4/scaling_governor
echo "userspace" > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
echo "userspace" > /sys/devices/system/cpu/cpufreq/policy4/scaling_governor

# Disable some cores
echo "0" > /sys/devices/system/cpu/cpu0/online
echo "0" > /sys/devices/system/cpu/cpu1/online
echo "0" > /sys/devices/system/cpu/cpu2/online
echo "0" > /sys/devices/system/cpu/cpu4/online
echo "0" > /sys/devices/system/cpu/cpu5/online
echo "0" > /sys/devices/system/cpu/cpu6/online


