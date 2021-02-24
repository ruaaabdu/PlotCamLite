####################################################
# accelerometer.py v0.3
# onAccelerationChange code taken from  Phidget example code for the 1041 0/0/3 Accelerometer
####################################################
"""
This code handles accelerometer functions
@author Ruaa Abdulmajeed
@date February 23rd, 2021
"""

# Phidget libraries for PhidgetSpatial 0/0/3 Basic 1041_0 Accelerometer
from Phidget22.Phidget import *
from Phidget22.Devices.Accelerometer import *

# A deque is a list where we can remove from beginning and end, writing will add to right and reading will take from the front
from collections import deque

# QtTest is required for delaying thread
from PyQt5 import QtTest

# PyQt Core for signals and threads
from PyQt5.QtCore import pyqtSignal, QThread

# Python Threading for write thread
from threading import Thread

class Position:
    """ This class is used to store the x and y coordinates."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        """Overwrites tostring function so that position can be printed

        Returns:
            str: x and y coordinates
        """
        return "(" + str(self.x) + ", " + str(self.y) + ")"

buffer = deque([]) # Initalize empty deque to write and read values from
def onAccelerationChange(self, acceleration, timestamp):
    x_acc = acceleration[0]
    y_acc = acceleration[1]
    pos = Position(x_acc, y_acc)
    buffer.append(pos)

def start_accelerometer():
    accelerometer0 = Accelerometer()
    accelerometer0.setOnAccelerationChangeHandler(onAccelerationChange)
    accelerometer0.openWaitForAttachment(1000)

    ### To Edit below ###
    try:
        input("")
    except (Exception, KeyboardInterrupt):
        print(Exception)
        pass
    accelerometer0.close()

class AccelerometerThread(QThread):  # reading thread, starts write thread
    """Accelerometer Thread runs the thread which handles the camera stream

    Args:
        QThread (QThread): Manages the thread
    """
    changeTarget = pyqtSignal(Position)
    # Needs to emit the signal everytime there is a change

    def __init__(self, parent=None):
        super(AccelerometerThread, self).__init__(parent)
        self.accelerometer_write_thread = Thread(target=start_accelerometer)
        self.runs = True

    def run(self):
        self.commence_working()
        self.stop()

    def stop(self):
        self.runs = False
        self.finished.emit()

    def commence_working(self):
        """ Runs the accelerometer write thread """
        self.accelerometer_write_thread.start()
        while self.runs == True:
            # If new_pos stores a coordinate  (look into reading/writing problem,
            # buffer is place to store/hold values, one thread will read one thread will write)
            if buffer:
                new_pos = buffer.popleft()
                self.changeTarget.emit(new_pos)
                QtTest.QTest.qWait(200)