import time
import cpu_usage
import serial

# Time to wait between logging a line in ms
DELAY=0.09

if __name__ == "__main__":	
	try:
		ser = serial.Serial(
			port="/dev/ttySAC2",\
			baudrate=115200,\
			parity=serial.PARITY_NONE,\
			stopbits=serial.STOPBITS_ONE,\
			bytesize=serial.EIGHTBITS,\
			timeout=0)
		print("Connected to: " + ser.portstr)
		connected = True
	except:
		print("Can't connect to serial. Skipping.")
		connected = False
	while True:
		temps = cpu_usage.getTemps()
		#print(temps)
		# -1 indicates get loads for all cpus
		# 0.05 indicates s interval for measurement
		usages = cpu_usage.getCpuLoad(-1, 0.1)
		#print(usages)
		line = ''
		for u in usages:
			line += ' ' + str(u)
		for t in temps:
			line += ' ' + str(t)
		ser.write(line)
		ser.write('\n\r')
		time.sleep(DELAY)
		
