from struct import unpack_from

handlers = {}

def registerHandler(HandlerClass):
	handler = HandlerClass()
	cmd = handler.getCommandID()
	handlers[cmd] = handler.parser

def runHandler(datagram):
	cmd = unpack_from("l",datagram,4)
	handlers[cmd](datagram[4:len(datagram)])
