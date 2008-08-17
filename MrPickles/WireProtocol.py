from struct import unpack_from

handlers = {}

def registerHandler(HandlerClass):
	handler = HandlerClass()
	cmd = handler.getCommandID()
	handlers[cmd] = handler.parser

def runHandler(datagram):
	cmd = unpack_from("ll",datagram)
	handlers[cmd[0]](cmd[1])
