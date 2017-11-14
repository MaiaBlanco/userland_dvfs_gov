import serial
import sys
import time

XU4_SERIAL = '/dev/ttyUSB0'
SMARTPOWER2_SERIAL = '/dev/ttyUSB1'
BAUD=115200
logfile='../data/temp_power_load_log.log'


try:
    xu4_ser = serial.Serial(
        port=XU4_SERIAL,\
        baudrate=BAUD,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
        timeout=0)
    sp2_ser = serial.Serial(
        port=SMARTPOWER2_SERIAL,\
        baudrate=BAUD,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
        timeout=0)
except:
    print("Failed to open one or both serial ports.")
    sys.exit(1)

# Clear the first few lines:
for i in range(4):
    xu4_ser.reset_input_buffer()
    sp2_ser.reset_input_buffer()
    xu4_line = xu4_ser.readline().strip()
    sp2_line = sp2_ser.readline().strip()


f = open(logfile, 'w')
f.write('u0 u1 u2 u3 u4 u5 u6 u7 t0 t1 t2 t3 tgpu v a w\n')
i = 0
data=''
while i < 100:
    char = ''
    while char != '\r':
        char = xu4_ser.read()
    char = ''
    while char != '\r':
        char = xu4_ser.read()
        if char != '\n' and char != '\r':
            data+=char
    #data.rstrip(' ')
    data += ' '    
    char = ''
    while char != '\r':
        char = sp2_ser.read()
    char = ''
    while char != '\r':
        char = sp2_ser.read()
        if char != '\n' and char != '\r':
            data+=char
    #data.rstrip(' ')
    data+='\n'
    #xu4_line = xu4_ser.readline().strip()
    #sp2_line = sp2_ser.readline().strip()
    #print(sp2_line)
#    if len(str(xu4_line)) > 0 and len(str(sp2_line)) > 0:
    #data = str(xu4_line) + ' ' + str(sp2_line) + '\n\r'
#    print(str(i) + ' '+ data, end="")
#    data.lstrip()
    f.write(data[1:])
    data = ''
    i += 1
    xu4_ser.reset_input_buffer()
    sp2_ser.reset_input_buffer()
    time.sleep(0.08)
f.close()
