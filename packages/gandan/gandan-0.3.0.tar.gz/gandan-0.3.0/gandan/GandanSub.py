import struct, sys, time, logging, traceback
import socket
import re
try:
	from .GandanMsg import *
except Exception as e:
	from gandan.GandanMsg import *
class GandanSub:
	def __init__(self, topic = "TEST", ip = '127.0.0.1', port = 59500, timeout = 1):
		self.ip_port = (ip, port)
		self.topic    = topic
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if timeout == 0:
			self.sock.setblocking(True)
		else:
			self.sock.settimeout(timeout)
		self.sock.connect(self.ip_port)
		msg = GandanMsg('S', self.topic, '')
		self.sock.send(bytes(msg))

	def sub_sync(self, cb):
		try:
			msg = GandanMsg.recv_sync(self.sock)
			try:
				cb(msg.topic,msg.data)
			except Exception as e:
				logging.info(f"callback error: {e}")
		except Exception as e:
			# logging.error(f"error: {e}")
			if str(e) == 'timed out':
				return None
			else:
			    raise Exception("connection lost")

	def close(self):
		self.sock.close()