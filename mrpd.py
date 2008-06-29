#!/usr/bin/env python

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

from MrPickles import WireProtocol

from MrPickles.CommandHandlers.Movement.Steering import Steering
from MrPickles.CommandHandlers.Movement.Acceleration import Acceleration
from MrPickles.CommandHandlers.Management.KeepAlive import KeepAlive

class PacketHandlerUDP(DatagramProtocol):
	def datagramReceived(self, datagram, address):
		WireProtocol.runHandler(datagram)
		
def main():	
	WireProtocol.registerHandler(KeepAlive)
	WireProtocol.registerHandler(Steering)
	WireProtocol.registerHandler(Acceleration)
	
	print WireProtocol.handlers
	
	reactor.listenUDP(6969, PacketHandlerUDP())
	reactor.run()


if __name__ == '__main__':
	main()
	
	



