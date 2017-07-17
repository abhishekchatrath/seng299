import socket
import threading
from ClientVariables import ClientVariables

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
	ConnectionDict = {}
	ChatroomDict = {}

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
			if len(self.ConnectionDict) < 20:
				print('Connection Received: %s' % str(address))
				threading.Thread(target=self.handle_connection, args=(client, address)).start()
			else:
				print("Max Capacity reached")
				client.send("Sorry, the maximum occupancy has been reached.")
				client.close()

	def set_alias(self, client):
		client.send("Please type your alias and press Enter: ")
		is_taken = True
		while is_taken:
			is_taken = False
			alias = client.recv(self.buf_size)
			for key in self.ConnectionDict:
				if self.ConnectionDict[key].alias == alias:
					client.send("That name has already been taken, please enter a new alias.")
					is_taken = True	
		client.send("Your alias is %s" %(alias))
		return alias
		
	def handle_server_admin(self):
		#handle creating/deleting rooms, blocking/unblocking clients
		while True:
			command = raw_input()

	def handle_connection(self, client, address):
		alias = self.set_alias(client)
		clientVariables = ClientVariables(alias,address,None)
		self.ConnectionDict[client] = clientVariables
		client.send("Type your message and press Enter to send. Type exit() to quit.")
		client.settimeout(None)
		
		while True:
			try:
				data = client.recv(self.buf_size)
				if data:
					print("%s:%s >> %s" % (address[0],address[1],data))
					message = self.ConnectionDict[client].alias + ": " + data
					for key in self.ConnectionDict:
						key.send(message)
				else:
					raise error('Client disconnected')
			except:
				print("Closed Client %s:%s" %(address[0],address[1]))
				del self.ConnectionDict[client]
				client.close()
				return False
				
if __name__ == "__main__":
    server = Server()
    server.run()
