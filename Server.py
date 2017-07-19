import socket
import threading
import os
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
			if len(self.ClientDict) < utils.MAX_CLIENTS:
				print('Connection Received: %s' % str(address))
				threading.Thread(target=self.handle_connection, args=(client, address)).start()
			else:
				print("Max Capacity reached")
				client.send("Sorry, the maximum capacity of %s users has already been reached. Please try again later." %(utils.MAX_CLIENTS))
				client.close()

	def set_alias(self, client, address):
		try:
			client.send("Please type your alias and press Enter:")
			is_taken = True
			while is_taken:
				is_taken = False
				alias = client.recv(self.buf_size)
				for key in self.ClientDict:
					if self.ClientDict[key].alias == alias:
						client.send("That name has already been taken, please enter a new alias.")
						is_taken = True
			client.send("Your alias is %s" %(alias))
			return alias
		except:
			self.close_client(client,address)

	def add_client_to_room(self, client, address):
		try:
			str = "Please join one of the following chatrooms by typing its name and pressing Enter:"
			for room in self.ChatroomDict:
				str += '\n' + room
			client.send(str + '\n')
			while True:
				room = client.recv(self.buf_size)
				if room in self.ChatroomDict.keys():
					self.ChatroomDict[room].add_client(client)
					client.send("You are now in the room: %s" %(room))
					return room
				else:
					client.send('%s is not a valid chatroom name. Please type a name from the list.' %(room))
		except:
			self.close_client(client,address)

	def handle_server_admin(self):
		#handle creating/deleting rooms, blocking/unblocking clients
		print("Please type one of the following commands and press Enter to execute it.")
		for command in utils.commands:
			print(command)
		print("")
		while True:
			try:
				command = raw_input()
				if utils.validate_cmd(command):
					if command == utils.commands[0]:#create_room
						self.create_room()
					# elif command == utils.commands[1]:#name_room
					# 	#todo after dinner
					elif command == utils.commands[2]:#del_room
						self.delete_room()
					# elif command == utils.commands[2]:#toggle_block
					# 	#todo after dinner
				else:
					print("Invalid command. Please try again.")
			except:
				self.sock.close()
				os._exit(1)

	def create_room(self):
		if len(self.ChatroomDict) < utils.MAX_ROOMS:
			try:
				print("Please type the name for the new room and press Enter.")
				room_name = raw_input()
				if utils.validate_str(room_name) and room_name not in self.ChatroomDict.keys():
					self.ChatroomDict[room_name] = ChatRoom(room_name)
					print("The room %s has been created" %(room_name))
				else:
					print("Invalid room name. Command has been aborted.")
			except:
				self.sock.close()
				os._exit(1)
		else:
			print("Sorry, the maximum room limit of %s has already been reached." % (utils.MAX_ROOMS))

	def delete_room(self):
		print("Type the name of the room you want to delete")

	def close_client(self,client,address):
		print("Closed Client %s:%s" %(address[0],address[1]))
		if client in self.ClientDict.keys():
			if self.ClientDict[client].chatroom:
				room = self.ClientDict[client].chatroom
				self.ChatroomDict[room].remove_client(client)
			del self.ClientDict[client]
		client.close()

	def send_to_room(self,client,message):
		formatted_message = self.ClientDict[client].alias + ": " + message
		room = self.ClientDict[client].chatroom
		for item in self.ChatroomDict[room].clientList:
			try:
				item.send(formatted_message)
			except:
				self.close_client(item,self.ClientDict[item].address)

	def handle_connection(self, client, address):
		clientVariables = ClientVariables(self.set_alias(client,address), address, self.add_client_to_room(client,address))
		self.ClientDict[client] = clientVariables
		try:
			client.send("Type your message and press Enter to send. Type exit() to quit.")
			client.settimeout(None)
			while True:
				data = client.recv(self.buf_size)
				if data:
					print("%s:%s >> %s" % (address[0],address[1],data))
					self.send_to_room(client, data)
				else:
					raise error('Client disconnected')
		except:
			self.close_client(client,address)
			return False

if __name__ == "__main__":
		server = Server()
		server.run()
