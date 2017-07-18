import socket
import threading
import utils
from ChatRoom import ChatRoom
from ClientVariables import ClientVariables

# TO DO:
# properly handle chatrooms and client list
# set up handle connections to deal with more than just messages
# create a packet breakdown and assembler
# listen for server admin commands and execute them appropriately
# change how data from client is handled using buffer

class Server():
	host = None
	port = None
	sock = None
	buf_size = None
	ClientDict = {}
	ChatroomDict = {}

	def __init__(self):
		self.host = utils.socket.get('HOST', '')
		self.port = utils.socket.get('PORT', 9000)
		self.buf_size = utils.BUFF_SIZE
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))
		self.ChatroomDict['General'] = ChatRoom('General')
		
	def run(self):
		print('Starting Server.')
		self.sock.listen(5)
		print('Server is listening...')
		threading.Thread(target=self.handle_server_admin).start()
		while True:
			client, address = self.sock.accept()
			if len(self.ClientDict) < 20:
				print('Connection Received: %s' % str(address))
				threading.Thread(target=self.handle_connection, args=(client, address)).start()
			else:
				print("Max Capacity reached")
				client.send("Sorry, the maximum occupancy has been reached.")
				client.close()
	
	#I think you can you use recursion here instead.
	def set_alias(self, client):
		client.send("Please type your alias and press Enter:")
		is_taken = True
		while is_taken:
			is_taken = False
			alias = client.recv(self.buf_size)
			for key in self.ClientDict:
				if self.ClientDict[key].alias == alias:
					client.send("That name has already been taken, please enter a new alias.\n")
					is_taken = True	
		client.send("Your alias is %s" %(alias))
		return alias
	
	def add_client_to_room(self, client):
		str = "Please choose one of our chatrooms and press Enter:\n"
		for room in ChatroomDict:
			str += room + '\n'
		while True:
			client.send(str)
			room = client.recv(self.buf_size)
			if utils.validate_str(room):
				return room
			client.send('That chat room does not exist, please choose a proper chat room.\n')	
		
	def handle_server_admin(self):
		#handle creating/deleting rooms, blocking/unblocking clients
		while True:
			#print("Please type an admin command and press Enter:\n")
			command = raw_input()
			if utils.validate_cmd(command):
				if command == utils.commands[0]:#create_room
					#print("Please type the name for the new room and press Enter:'n")
					room_name = raw_input()
					ChatroomDict[room_name] = ChatRoom(room_name)
				if command == utils.commands[1]:#name_room
					#todo after dinner
				if command == utils.commands[2]:#del_room
					#todo after dinner
				if command == utils.commands[2]:#toggle_block
					#todo after dinner
			else:
				#print to stdout (for server admin) invalid cmd
				
	def handle_connection(self, client, address):
		clientVariables = ClientVariables(self.set_alias(client), address, self.add_client_to_room(client))
		self.ClientDict[client] = clientVariables
		client.send("Type your message and press Enter to send. Type exit() to quit.")
		client.settimeout(None)
		
		while True:
			try:
				data = client.recv(self.buf_size)
				if data:
					print("%s:%s >> %s" % (address[0],address[1],data))
					message = self.ClientDict[client].alias + ": " + data
					for key in self.ClientDict:
						key.send(message)
				else:
					raise error('Client disconnected')
			except:
				print("Closed Client %s:%s" %(address[0],address[1]))
				del self.ClientDict[client]
				client.close()
				return False
				
if __name__ == "__main__":
    server = Server()
    server.run()
