
from time import sleep

from Phidgets.PhidgetException import * 
from Phidgets.Events.Events import *
from Phidgets.Devices.Servo import Servo

servo = Servo()
servo.openPhidget()

servo.waitForAttach(10000)
x=0
while True:
	if x > 200:
		break
	x = x + 1
	servo.setPosition(0,x)

