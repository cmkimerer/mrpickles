from MrPickles.CommandHandlers.BaseHandler import BaseHandler
from MrPickles.Controller.PhidgetMovement import PhidgetMovement
from struct import unpack_from

class BaseMovement(BaseHandler):
	def __init__(self):
		self.PhidgetMovement = PhidgetMovement(self.SERVO_ID)
		
	
	def parser(self,boogz):
		change = unpack_from("l",boogz)
		self.PhidgetMovement.setValue(change)