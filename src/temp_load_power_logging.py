import serial
import time
import cpu_usage

# Time to wait between logging a line in ms
DELAY=1

if __name__ == "__main__":
	try:
		ser = serial.Serial(
			port="/dev/ttyUSB0",\
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
		print(temps)
		# -1 indicates get loads for all cpus
		# 0.05 indicates s interval for measurement
		usages = cpu_usage.getCpuLoad(-1, 0.05)
		print(usages)
		if connected:
			line=''
			#ser.reset_input_buffer()
			char = ''
			while char != '\n':
				char = ser.read(1)
			char = ''
			while char != '\n':
				char = ser.read(1)
				line += char
			vaw = line.strip().split(' ')
			print(vaw)
			vaw = [float(x[2:]) for x in vaw]
			print(vaw)
		time.sleep(DELAY)
		
