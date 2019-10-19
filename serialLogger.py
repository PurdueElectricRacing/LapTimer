import os
import serial
import sys

try:
    port = str(sys.argv[1])
except:
    port = '/dev/cu.usbmodem14101'
print('Type \'s\' to start the serial logging on port ' + port)
inputChar = raw_input('> ')
while inputChar != 's':
    if inputChar == 'q':
        sys.exit()
    inputChar = raw_input('> ')
with open('lapTimes.txt', 'w+') as fh:
    try:
        serialStream = serial.Serial(port, 9600)
    except:
        print('Failed to open port ' + port + '!')
        sys.exit()
    while True:
        line = serialStream.readline()
        line = line.decode('utf-8')
        print(line)
        fh.write(line)
