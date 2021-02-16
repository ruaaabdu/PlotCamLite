#############################################################################
# ruaa Cpde taken from Phidget example code for the 1041 0/0/3 Accelerometer
#############################################################################

from Phidget22.Phidget import *
from Phidget22.Devices.Accelerometer import *

# a list where we can remove from beginning and end, writing will add to right and reading will take from the front
from collections import deque
qt_thread = None


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

#buffer = deque([Position(0, 0), Position(1, 1), Position(1, 2), Position(1, 3),\
# Position(1, -2), Position(-2, -2), Position(-1, 1)])
buffer = deque([])
def onAccelerationChange(self, acceleration, timestamp):

    x_acc = acceleration[0]
    y_acc = acceleration[1]
    pos = Position(x_acc, y_acc)
    print("WRITE" + str(pos))
    #print(pos)
    

    buffer.append(pos)

    if x_acc >= -0.05 and x_acc <= 0.05 and y_acc >= -0.05 and y_acc <= 0.05:
        print("Camera is level")

    #print(buffer)

    # qt_thread.changeTarget.emit(pos)

    # print("X Acceleration: \t" + str(x_acc))
    # print("X Acceleration: \t" + str(y_acc))

    # if x_acc >= -0.05 and x_acc <= 0.05 and y_acc >= -0.05 and y_acc <= 0.05:
    #     print("Camera is level")
    # print("Timestamp: " + str(timestamp))
    # print("----------")


def start_accelerometer():
    accelerometer0 = Accelerometer()
    accelerometer0.setOnAccelerationChangeHandler(onAccelerationChange)
    accelerometer0.openWaitForAttachment(5000)

    try:
        input("Press Enter to Stop\n")
    except (Exception, KeyboardInterrupt):
        print(Exception)
        pass
    accelerometer0.close()

