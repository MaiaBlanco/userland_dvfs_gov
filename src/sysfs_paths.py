# This file defines strings as sysfs paths for various
# dials and control knobs available in Debian.
# fn_ prefix indicates that the string should be formatted with a
# core number

# For each cpu core
fn_cpu_core_base="/sys/devices/system/cpu/cpu{}/cpufreq/"
fn_cpu_cluster=fn_cpu_core_base+"related_cpus"
fn_cpu_max_freq=fn_cpu_core_base+"cpuinfo_max_freq"
fn_cpu_min_freq=fn_cpu_core_base+"cpuinfo_min_freq"
fn_cpu_freq_read=fn_cpu_core_base+"cpuinfo_cur_freq"
fn_cpu_governor=fn_cpu_core_base+"scaling_governor"
fn_cpu_max_freq_set=fn_cpu_core_base+"scaling_max_freq"
fn_cpu_min_freq_set=fn_cpu_core_base+"scaling_min_freq"
fn_cpu_freq_set=fn_cpu_core_base+"scaling_cur_freq"
fn_core_enabled=fn_cpu_core_base[:-8]+"online"

# for clusters (e.g. policies on whole clusters):
fn_cluster_base="/sys/devices/system/cpu/cpufreq/policy{}/"
fn_cluster_max=fn_cluster_base+"cpuinfo_max_freq"
fn_cluster_min=fn_cluster_base+"cpuinfo_min_freq"
fn_cluster_freq_range=fn_cluster_base+"cpuinfo_available_frequencies"
fn_cluster_cpus=fn_cluster_base+"affected_cpus"
#fn_cluster_govs=fn_cluster_base+"scaling_cur_governor"
fn_cluster_gov=fn_cluster_base+"scaling_governor"
fn_cluster_freq_read=fn_cluster_base+"cpuinfo_cur_freq"
fn_cluster_freq_set=fn_cluster_base+"scaling_setspeed"
fn_cluster_max_set=fn_cluster_base+"scaling_max_freq"
fn_cluster_min_set=fn_cluster_base+"scaling_min_freq"


