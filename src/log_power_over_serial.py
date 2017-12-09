import serial
import sys
import time
from platform import system
import atexit

f = None

def cleanup():
    if f is not None:
        f.close()
    sp2_ser.close()

#target inter sample delay (seconds):
INTER_SAMPLE_TIME = 0.09

IS_WINDOWS = system().lower() == "windows"
if (IS_WINDOWS):
    SMARTPOWER2_SERIAL='COM6'#'COM4'
else:
    SMARTPOWER2_SERIAL = '/dev/ttyUSB0'
BAUD=115200
logfile='../data/smartpower2_{}.log'

atexit.register(cleanup)

try:
    print("Attempting connection to {}".format(SMARTPOWER2_SERIAL))
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
    #xu4_ser.reset_input_buffer()
    sp2_ser.reset_input_buffer()
    #xu4_line = xu4_ser.readline().strip()
    sp2_line = sp2_ser.readline().strip()

curr_time = time.strftime("%d-%m-%Y",time.localtime())
f = open(logfile.format(curr_time), 'w')
f.write('time v a w\n')
while True:
    curr_time = time.time()
    data = str(curr_time)
    data += ' '    
    char = ''
    while char != '\r':
        char = sp2_ser.read()
    char = ''
    while char != '\r':
        char = sp2_ser.read()
        if char != '\n' and char != '\r':
            data+=char
    data+='\n'
    f.write(data[1:])
    print(data)
    i += 1
    #sp2_ser.reset_input_buffer()
    elapsed = time.time() - curr_time
    time.sleep( max(0, INTER_SAMPLE_TIME - elapsed) )
