import pygtk
pygtk.require('2.0')
import gtk
import gobject
from socket import *
from struct import pack


FORWARD = 65362
REVERSE = 65364
LEFT = 65361
RIGHT = 65363

class SampleClient:

	def __init__(self, ip, port):
		self.addr = (ip, port)
		self.current_speed = 0
		self.current_direction = 0
		
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect('destroy', self.destroy)
		self.window.connect('key_press_event', self.key_pressed)
		self.window.connect('key_release_event', self.key_released)
	
		self.hbox = gtk.HBox(False, 0)
		self.dbox = gtk.VBox(False, 0)
		self.tbox = gtk.VBox(False, 0)

		self.speed_desc_label = gtk.Label("Forward/Reverse")
		self.turn_desc_label = gtk.Label("Left/Right")

		self.speed_label = gtk.Label("0%")
		self.turn_label = gtk.Label("0%")
		
		self.window.add(self.hbox)

		self.hbox.pack_start(self.dbox, True, True, 5)
		self.hbox.pack_start(self.tbox, True, True, 5)

		self.dbox.pack_start(self.speed_desc_label, True, True, 5)
		self.dbox.pack_start(self.speed_label, True, True, 5)
		self.tbox.pack_start(self.turn_desc_label, True, True, 5)
		self.tbox.pack_start(self.turn_label, True, True, 5)

		self.hbox.show()
		self.dbox.show()
		self.tbox.show()
		self.speed_desc_label.show()
		self.speed_label.show()
		self.turn_desc_label.show()
		self.turn_label.show()

		self.sock = socket(AF_INET,SOCK_DGRAM)
		gobject.idle_add(self.send_information)

		self.window.show()

	def main(self):
		gtk.main()

	def destroy(self, widget, data=None):
		gtk.main_quit()

	def key_pressed(self, widget, data):
		key = data.keyval

		if key == FORWARD:
			self.change_speed(5)
		elif key == REVERSE:
			self.change_speed(-5)
		elif key == LEFT:
			self.change_direction(-5)
		elif key == RIGHT:
			self.change_direction(5)

	def change_speed(self, delta):
		#self.set_if_valid(self.current_speed, self.current_speed + delta)
		new_speed = self.current_speed + delta
		if new_speed <= 100 and new_speed >= -100:
			self.current_speed = new_speed
			self.update_speed_label()

	def change_direction(self, delta):
		#self.set_if_valid(self.current_direction, self.current_direction + delta)
		new_direction = self.current_direction + delta
		if new_direction <= 100 and new_direction >= -100:
			self.current_direction = new_direction
			self.update_direction_label()

	def set_if_valid(self, thing_to_set, value_to_set):
		print value_to_set
		if value_to_set <= 100 and value_to_set >= -100:
			thing_to_set = value_to_set

	def key_released(self, widget, data):
		key = data.keyval	
		
		if key == FORWARD or key == REVERSE:
			self.current_speed = 0
			self.update_speed_label()
		elif key == LEFT or key == RIGHT:
			self.current_direction = 0
			self.update_direction_label()

	def update_speed_label(self):
		text = str(self.current_speed) + '%'
		self.speed_label.set_text(text)
	
	def update_direction_label(self):
		text = str(self.current_direction) + '%'
		self.turn_label.set_text(text)

	def send_information(self):
		if self.current_speed == 0 and self.current_direction == 0:
			return True

		#do network send here
		speed = pack("ll", 2001, self.current_speed)
		direction = pack("ll", 2000, self.current_direction)
		self.sock.sendto(speed,self.addr)
		self.sock.sendto(direction, self.addr)

		return True

if __name__ == "__main__":
	client = SampleClient("192.168.2.12", 6969)
	client.main()


