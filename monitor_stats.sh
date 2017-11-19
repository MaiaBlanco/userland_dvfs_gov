#!/bin/bash
# print the cpu temperature 
for i in {0..4};
do
TEMP=`cat /sys/devices/virtual/thermal/thermal_zone${i}/temp`
echo Temp $i: ${TEMP:0:2}.${TEMP:2:4} Celcius
done
#echo `cut -b 1-2 <<< $TEMP` Celcius
#echo Cooling 0:
#cat /sys/devices/virtual/thermal/cooling_device0/cur_state
#echo Cooling 1:
#cat /sys/devices/virtual/thermal/cooling_device1/cur_state
#echo Fan PWM:
#cat /sys/devices/odroid_fan.14/pwm_duty
for i in {0..7};
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
echo Available CPU Governors:
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors
echo Avail. Freqs. for Cluster 1:
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies
echo C1 gov: `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor`
echo Avail. Freqs. for Cluster 2:
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies
echo C2 gov: `cat /sys/devices/system/cpu/cpu4/cpufreq/scaling_governor`
FREQ=`cat /sys/devices/platform/11800000.mali\:/devfreq/11800000.mali\:/cur_freq`
echo GPU Freq: $FREQ
