import sys
import os
import random
import serial
import glob
import threading
import time
import gc
from threading import Timer, Thread
from PySide2.QtWidgets import (QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QGridLayout, QLineEdit, QSpacerItem, QRadioButton, QGroupBox, QProgressBar, QComboBox)
from PySide2 import QtCore
from PySide2.QtCore import Signal, Slot

class mainScreen(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.setWindowTitle('PER Lap Timer')

        self.connectionStatus = 'Disconnected'
        self.stopEvent = threading.Event()
        self.lastLapNumber = 0
        self.lastLapTime = 0

        self.connectionLabel = QLabel(self.connectionStatus)
        self.connectButton = QPushButton('Connect')
        self.lapNumberLabel = QLabel('Lap Number')
        self.lapTimeLabel = QLabel('Lap Time')
        self.lapNumber = QLabel('')
        self.lapTime = QLabel('')
        self.filler = QLabel(' ')
        self.portBox = QComboBox()
        self.portBox.addItem('Port')

        self.layout = QGridLayout()

        self.layout.addWidget(self.connectionLabel, 0, 0, 1, 2)
        self.layout.addWidget(self.lapNumberLabel, 1, 0, 1, 1)
        self.layout.addWidget(self.lapTimeLabel, 1, 4, 1, 1)
        self.layout.addWidget(self.lapNumber, 2, 0, 1, 1)
        self.layout.addWidget(self.lapTime, 2, 4, 1, 1)
        self.layout.addWidget(self.filler, 3, 0, 1, 4)
        self.layout.addWidget(self.portBox, 5, 0, 1, 3)
        self.layout.addWidget(self.connectButton, 5, 4, 1, 2)

        self.setLayout(self.layout)
        self.connectButton.clicked.connect(self.connect)
        self.portBox.activated.connect(self.comboHandler)

        self.findThread = threading.Thread(name='portFind', target=self.findPorts)
        self.findThread.setDaemon(True)
        self.findThread.start()

    def findPorts(self):
        while True:
            oldPorts = []
            if sys.platform.startswith('win'):
                ports = ['COM%s' % (i + 1) for i in range(256)]
            elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                ports = glob.glob('/dev/tty[A-Za-z]*')
            elif sys.platform.startswith('darwin'):
                ports = glob.glob('/dev/tty.*')
            else:
                raise EnvironmentError('Unsupported platform')

            if oldPorts != ports:
                self.portBox.clear()
                self.portBox.addItem('Port')
                for port in ports:
                    self.portBox.addItem(port)
                try:
                    index = self.portBox.findText(self.port)
                except:
                    index = 0
                self.portBox.setCurrentIndex(index)

            oldPorts = ports
            time.sleep(5)

    def setStatusLabel(self):
        self.connectionLabel.setText(self.connectionStatus)

    def connect(self):
        try:
            self.serialStream = serial.Serial(self.port, 9600, timeout=10)
        except:
            self.connectionLabel.setText('Could not connect to lap timer!')
            t = Timer(3, self.setStatusLabel)
            t.start()

            return None
        self.connectionStatus = 'Connected'
        self.connectionLabel.setText(self.connectionStatus)
        self.connectButton.setText('   Stop   ')
        self.connectButton.clicked.connect(self.stop)
        self.stopEvent.clear()

        self.daemonRead = threading.Thread(name='serialRead', target=logSerial, args=(self,))
        self.daemonRead.setDaemon(True)
        self.daemonRead.start()

    def stop(self):
        self.stopEvent.set()
        try:
            self.serialStream.close()
        except:
            None
        self.connectionStatus = 'Disconnected'
        self.connectionLabel.setText('Device disconnected')
        self.connectButton.setText('Connect')
        self.connectButton.clicked.connect(self.connect)
        t = Timer(3, self.setStatusLabel)
        t.start()

    def comboHandler(self, index):
        self.port = self.portBox.itemText(index)

def logSerial(window):
    if window.stopEvent.isSet():
        return None
    line = []
    line.append('Lap Times\n')
    line.append('-=-=-=-=-\n')

    while not window.stopEvent.isSet():
        try:
            newline = window.serialStream.readline()
            newline = newline.decode('utf-8')
            line.append(newline)
            print(newline)
            if newline[0] == 'L':
                colonPos = newline.find(':')
                if (colonPos - 1) == 1:
                    lap = newline[1]
                else:
                    lap = newline[1:(colonPos - 1)]
                time = newline[(colonPos + 1):len(newline)]
                window.lapNumber.setText('#' + lap)
                window.lapTime.setText(time.strip('\n') + 'seconds')
            elif newline[0] == 'C':
                self.connectionLabel.setText('Calibration Complete')
                t = Timer(5, self.setStatusLabel)
                t.start()
        except:
            None
    
    try:
        window.serialStream.close()
    except:
        return None

    iteration = 0
    while os.path.isfile('lapTimes' + str(iteration) + '.txt'):
        iteration = iteration + 1
    with open('lapTimes' + str(iteration) + '.txt', 'w+') as fh:
        for toWrite in line:
            fh.write(toWrite)

if __name__ == '__main__':
    main = QApplication(sys.argv)
    window = mainScreen()
    window.setFixedSize(400, 175)

    window.show()

    main.exec_()
    sys.exit()