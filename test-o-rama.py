
from time import sleep

from Phidgets.PhidgetException import * 
from Phidgets.Events.Events import *
from Phidgets.Devices.Servo import Servo

servo = Servo()
servo.openPhidget()

servo.waitForAttach(10000)
#`sleep(0.5)
#servo.setPosition(0,200)
#sleep(0.5)
servo.setPosition(0,100)
sleep(1)
servo.setPosition(0,100)
