from MrPickles.CommandHandlers.BaseHandler import BaseHandler
from MrPickles.Controller.PhidgetMovement import PhidgetMovement
from struct import unpack_from

class BaseMovement(BaseHandler):
	def __init__(self):
		self.PhidgetMovement = PhidgetMovement(self.SERVO_ID)
		
	
	def parser(self,boogz):
		if type(boogz) is str:
			change = unpack_from("l",boogz)
		else:
			change = boogz
		self.PhidgetMovement.setValue(change)
