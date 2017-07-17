import socket
import threading

# TO DO:
# properly handle chatrooms and client list
# set up handle connections to deal with more than just messages
# create a packet breakdown and assembler
# listen for server admin commands and execute them appropriately

class Server():
	host = 9000
	port = None
	sock = None
	buf_size = None
	ConnectionList = {}

	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.host = ''
		self.port = 9000
		self.buf_size = 1024
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))
		
	def run(self):
		print('Starting Server.')
		self.sock.listen(5)
		print('Server is listening...')
		threading.Thread(target=self.handle_server_admin).start()
		while True:
			client, address = self.sock.accept()
			client.send("Please type your alias and press Enter: ")
			alias = client.recv(self.buf_size)
			client.send("Type your message and press Enter to send. Type exit() to quit.")
			self.ConnectionList[client] = alias 
			client.settimeout(None)
			print('Connection Received: %s' % str(address))
			threading.Thread(target=self.handle_connection, args=(client, address)).start()
			
	def handle_server_admin(self):
		#handle creating/deleting rooms, blocking/unblocking clients
		while True:
			command = raw_input()

	def handle_connection(self, client, address):
		while True:
			try:
				data = client.recv(self.buf_size)
				if data:
					print("%s:%s >> %s" % (address[0],address[1],data))
					message = self.ConnectionList[client] + ": " + data
					for key in self.ConnectionList:
						key.send(message)
				else:
					raise error('Client disconnected')
			except:
				print("Closed Client %s:%s" %(address[0],address[1]))
				del self.ConnectionList[client]
				client.close()
				return False
				
if __name__ == "__main__":
    server = Server()
    server.run()
