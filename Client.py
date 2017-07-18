import socket 
import time
import threading
import sys
import utils

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

	def __init__(self):
		self.server_host = socket.gethostname()
		self.server_port = utils.socket.get('PORT', 9000)
		self.buf_size = utils.BUFF_SIZE
		self.server_address = (self.server_host,self.server_port)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	def run(self):
		self.sock.connect(self.server_address) 
		print("Successfully connected to chat server")
		threading.Thread(target=self.send).start()
		threading.Thread(target=self.recv).start()
		
	def send(self):
		while True:
			try:
				msg = raw_input()
				if msg == 'exit()':
					raise Exception
				self.sock.send(msg)
			except:
				self.sock.shutdown(socket.SHUT_RDWR)
				self.sock.close()
				return False
				
	def recv(self):
		while True:
			data = self.sock.recv(1024)
			if data:
				print("%s" %(data))
			else:
				return False
	

if __name__ == "__main__":
    client = Client()
    client.run()