import socket
import time
import datetime
import threading
import sys
import os
import utils

from Parser import Parser
#TO DO:
# write a Client Parser that breaks down and assembles packets
# change send and receive to handle more than just messages
# create client attributes alias and chatroom
# create a GUI on the client side and listen for changes in that instead of in stdin, and update GUI with what server sends

class Client():
	server_host = None
	server_port = None
	server_address = None
	buf_size = None
	sock = None
	alias = None
	room = None

	def __init__(self):
		self.server_host = socket.gethostname()
		self.server_port = utils.socket.get('PORT', 9000)
		self.buf_size = utils.BUFF_SIZE
		self.server_address = (self.server_host,self.server_port)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def run(self):
		try:
			self.sock.connect(self.server_address)
			print("Successfully connected to chat server")
		except:
			print("Could not connect to server")
			os._exit(1)
		threading.Thread(target=self.send).start()
		threading.Thread(target=self.recv).start()

	def assemble_packet(self,msg):
		parser = Parser()
		message = msg.split(' ',1)
		command = message[0]
		print("command is %s" %(command))
		body = message[1]
		print("body is %s" %(body))
		if command == "message":
			date = datetime.datetime.now().strftime(utils.DATE_FORMAT)
			packet = parser.assemble(utils.codes["send_msg"],self.alias,self.room,date,body)
		elif command == "alias":
			packet = parser.assemble(utils.codes["set_alias"],body,"","","")
		elif command == "room":
			packet = parser.assemble(utils.codes["set_room"],self.alias,body,"","")
		elif command == "roomlist":
			packet = parser.assemble(utils.codes["get_roomlist"],self.alias,"","","")
		print("Sending packet %s" %(packet))
		return packet

	def send(self):
		while True:
			try:
				msg = raw_input()
				packet = self.assemble_packet(msg)
				if msg == 'exit()':
					raise Exception
				self.sock.send(packet)
			except Exception as e:
				print(e.message)
				self.sock.shutdown(socket.SHUT_RDWR)
				self.sock.close()
				os._exit(1)
				return False

	def breakdown_packet(self,packet):
		parser = Parser()
		parser.breakdown(packet)
		if parser.code == utils.codes["recv_msg"]:
			print("message recieved: %s" %(parser.body))
		elif parser.code == utils.codes["recv_roomlist"]:
			print("roomlist: %s" % (parser.body))
		elif parser.code == utils.codes["alias_success"]:
			self.alias = parser.alias
			print("alias successful: %s" % (parser.alias))
		elif parser.code == utils.codes["alias_invalid"]:
			print("alias invalid: %s" %(parser.alias))
		elif parser.code == utils.codes["room_success"]:
			self.room = parser.room
			print("room successful: %s" %(parser.room))
		elif parser.code == utils.codes["room_invalid"]:
			print("room invalid: %s" % (parser.room))
		else:
			print("Invalid packet recieved")

	def recv(self):
		while True:
			try:
				packet = self.sock.recv(1024)
				if packet:
					self.breakdown_packet(packet)
				else:
					raise Exception
			except:
				self.sock.shutdown(socket.SHUT_RDWR)
				self.sock.close()
				os._exit(1)
				return False

if __name__ == "__main__":
    client = Client()
    client.run()
