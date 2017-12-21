#!/bin/bash
# print the cpu temperature 
TEMP0=`cat /sys/devices/virtual/thermal/thermal_zone0/temp`
TEMP1=`cat /sys/devices/virtual/thermal/thermal_zone3/temp`
TEMP2=`cat /sys/devices/virtual/thermal/thermal_zone2/temp`
TEMP3=`cat /sys/devices/virtual/thermal/thermal_zone1/temp`
TEMP4=`cat /sys/devices/virtual/thermal/thermal_zone4/temp`
echo Core 4: ${TEMP0:0:2}.${TEMP0:2:4} Celcius
echo Core 5: ${TEMP1:0:2}.${TEMP1:2:4} Celcius
echo Core 6: ${TEMP2:0:2}.${TEMP2:2:4} Celcius
echo Core 7: ${TEMP3:0:2}.${TEMP3:2:4} Celcius
echo GPU: ${TEMP4:0:2}.${TEMP4:2:4} Celcius
#echo `cut -b 1-2 <<< $TEMP` Celcius
#echo Cooling 0:
#cat /sys/devices/virtual/thermal/cooling_device0/cur_state
#echo Cooling 1:
#cat /sys/devices/virtual/thermal/cooling_device1/cur_state
#echo Fan PWM:
#cat /sys/devices/odroid_fan.14/pwm_duty
for i in {0,4};
do
FREQ=`cat /sys/devices/system/cpu/cpu$i/cpufreq/cpuinfo_cur_freq`
FREQ2=`cat /sys/devices/system/cpu/cpu$i/cpufreq/scaling_cur_freq`
#GOV=`cat /sys/devices/system/cpu/cpu$i/cpufreq/scaling_governor`
echo CPU$i Freq: $FREQ kHz
echo CPU$i Freq_scaling: $FREQ2 kHz
#echo CPU$i Governor: $GOV
done
echo Enabled CPUS:
cat /sys/devices/system/cpu/online
#echo MEM Freq:
# Below only worked on android
#cat /sys/devices/platform/exynos5-devfreq-mif/devfreq/exynos5-devfreq-mif/cur_freq
#echo Available CPU Governors:
#cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors
echo Avail. Freqs. for Cluster 1:
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies
echo C1 gov: `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor`
echo Avail. Freqs. for Cluster 2:
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies
echo C2 gov: `cat /sys/devices/system/cpu/cpu4/cpufreq/scaling_governor`
FREQ=`cat /sys/devices/platform/11800000.mali/devfreq/devfreq0/device/devfreq/devfreq0/cur_freq`
echo GPU Freq: $FREQ

#VDD1=`cat /sys/devices/platform/pwrseq:/subsystem/devices/s2mps11-regulator/regulator/regulator.44/microvolts`
#echo Little Voltage: $VDD1 uVolts
#VDD2=`cat /sys/devices/platform/pwrseq:/subsystem/devices/s2mps11-regulator/regulator/regulator.40/microvolts`
#echo Little Voltage: $VDD2 uVolts

gpu_voltage=`cat /sys/devices/platform/pwrseq/subsystem/devices/s2mps11-regulator/regulator/regulator.42/microvolts`
mem_voltage=`cat /sys/devices/platform/pwrseq/subsystem/devices/s2mps11-regulator/regulator/regulator.43/microvolts`
echo GPU_V: $gpu_voltage
echo MEM_V: $mem_voltage

