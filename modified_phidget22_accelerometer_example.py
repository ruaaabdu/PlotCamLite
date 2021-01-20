#############################################################################
# Code taken from Phidget example code for the 1041 0/0/3 Accelerometer
#############################################################################

from Phidget22.Phidget import *
from Phidget22.Devices.Accelerometer import *

#Declare any event handlers here. These will be called every time the 
# associated event occurs.

def onAccelerationChange(self, acceleration, timestamp):

	x_acc = acceleration[0]
	y_acc = acceleration[1]

	print("X Acceleration: \t"+ str(x_acc))
	print("X Acceleration: \t"+ str(y_acc))

	if x_acc >= -0.05 and x_acc <= 0.05 and y_acc >= -0.05 and y_acc <= 0.05:
		print("Camera is level")
	print("Timestamp: " + str(timestamp))
	print("----------")

def main():
	accelerometer0 = Accelerometer()
	accelerometer0.setOnAccelerationChangeHandler(onAccelerationChange)
	accelerometer0.openWaitForAttachment(5000)

	try:
		input("Press Enter to Stop\n")
	except (Exception, KeyboardInterrupt):
		pass

	accelerometer0.close()

main()
