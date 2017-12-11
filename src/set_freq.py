import cpu_usage

print("Make sure system is running userspace before trying to set frequency!")
while True:
	freq = float(raw_input("Enter frequency in GHz: "))
	cpu_usage.setClusterFreq(0, int(freq*1000000))
	cpu_usage.setClusterFreq(4, int(freq*1000000))
