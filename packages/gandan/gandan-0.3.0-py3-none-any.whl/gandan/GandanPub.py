#--*--encoding:utf-8--*--
import struct, sys, time, logging, traceback
import socket
import re
try:
	from .GandanMsg import *
except Exception as e:
	from gandan.GandanMsg import *

class GandanPub:
	def __init__(self, topic = "TEST", ip = '127.0.0.1', port = 59500):
		self.ip_port = (ip, port)
		self.topic = topic
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect(self.ip_port)

	def pub_sync(self, data):
		try:
			msg = GandanMsg('P', self.topic, data)
			self.sock.send(bytes(msg))
		except Exception as e:
			logging.info(f"error: {e}")
			raise Exception("connection lost")

	def close(self):
		self.sock.close()