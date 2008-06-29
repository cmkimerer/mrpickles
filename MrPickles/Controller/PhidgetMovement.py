from Phidgets.PhidgetException import * 
from Phidgets.Events.Events import * 
from Phidgets.Devices.Servo import Servo

class PhidgetMovement:			
	def __init__(self,serial):
		self.servo = Servo()
		self.servo.openPhidget(serial)	
		print "connecting to servo: " + str(serial)
		self.servo.waitForAttach(10000)
		
	def setValue(self,value):
		pass
