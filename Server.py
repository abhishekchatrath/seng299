import socket
import threading
import os
import utils
from Parser import Parser
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
		self.host = "127.0.0.1"
		self.port = utils.socket.get('PORT', 9000)
		self.buf_size = utils.BUFF_SIZE
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))
		self.ChatroomDict['General'] = ChatRoom(utils.GEN_ROOM)

	def run(self):
		print('Starting Server.')
		self.sock.listen(5)
		print('Server is listening...')
		threading.Thread(target=self.handle_server_admin).start()
		while True:
			client, address = self.sock.accept()
			if len(self.ClientDict) < utils.MAX_CLIENTS:
				print('Connection Received: %s' % str(address))
				clientVariables = ClientVariables("",address,"")
				self.ClientDict[client] = clientVariables
				threading.Thread(target=self.handle_connection, args=(client, address)).start()
			else:
				print("Max Capacity reached")
				client.send("Sorry, the maximum capacity of %s users has already been reached. Please try again later." %(utils.MAX_CLIENTS))
				client.close()

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
						
					elif command == utils.commands[2]:#del_room
						self.delete_room()
					# elif command == utils.commands[2]:#toggle_block
						
				else:
					print("Invalid command. Please try again.")
			except Exception as e:
				print(str(e))
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
		if len(self.ChatroomDict) > utils.MIN_ROOMS:
			try:
				print("Type the name of the room you want to delete:")
				room_name = raw_input()
				if utils.validate_str(room_name) and (room_name in self.ChatroomDict) and (room_name != utils.GEN_ROOM):
					client_list = self.ChatroomDict[room_name].clientList
					print('Closing all clients in room %s' % (room_name))
					for client in client_list:
						self.close_client(client, self.ClientDict[client].address)
					del self.ChatroomDict[room_name]
					print('The room %s as been deleted.' % (room_name))
			except Exception as e:#for clean exit when user types CTRL+C
				print(str(e))
				self.sock.close()
				os._exit(1)
		else:
			print("Sorry, the minimum room limit has already been reached.")
	
	def close_client(self,client,address):
		print("Closed Client %s:%s" %(address[0],address[1]))
		if client in self.ClientDict.keys():
			if self.ClientDict[client].chatroom:
				room = self.ClientDict[client].chatroom
				self.ChatroomDict[room].remove_client(client)
			del self.ClientDict[client]
		client.shutdown(socket.SHUT_RDWR)
		client.close()

	def set_alias(self, client, parser):
		try:
			if utils.validate_str(parser.alias):
				for key in self.ClientDict:
					if self.ClientDict[key].alias == parser.alias:
						packet = parser.assemble(utils.codes["alias_invalid"],parser.alias,"","","")
						client.send(packet)
						return
				room_list = ""
				for room in self.ChatroomDict.keys():
					room_list += room + " "
				self.ClientDict[client].alias = parser.alias
				packet = parser.assemble(utils.codes["alias_success"],self.ClientDict[client].alias,"","",room_list)
				client.send(packet)
			else:
				packet = parser.assemble(utils.codes["alias_invalid"],parser.alias,"","","")
				client.send(packet)
		except:
			self.close_client(client,self.ClientDict[client].address)

	def add_client_to_room(self, client, parser):
		try:
			if parser.room in self.ChatroomDict.keys():
				self.ChatroomDict[parser.room].add_client(client)
				self.ClientDict[client].chatroom = parser.room
				packet = parser.assemble(utils.codes["room_success"],self.ClientDict[client].alias,self.ClientDict[client].chatroom,"","")
				client.send(packet)
			else:
				packet = parser.assemble(utils.codes["room_invalid"],self.ClientDict[client].alias,parser.room,"","")
				client.send(packet)
		except:
			self.close_client(client,self.ClientDict[client].address)

	def send_room_list(self,client,parser): #roomlist is sent as space-separated string
		try:
			room_list = ""
			for room in self.ChatroomDict.keys():
				room_list += room + " "
			packet = parser.assemble(utils.codes["recv_roomlist"],self.ClientDict[client].alias,"","",room_list)
			client.send(packet)
		except:
			self.close_client(client,self.ClientDict[client].address)

	def send_to_room(self,client,parser):
		formatted_message = parser.date + " " + self.ClientDict[client].alias + ": " + parser.body
		packet = parser.assemble(utils.codes["recv_msg"],self.ClientDict[client].alias,self.ClientDict[client].chatroom,"",formatted_message)
		room = self.ClientDict[client].chatroom
		print "Length is" + str(len(self.ClientDict))
		for person in self.ChatroomDict[room].clientList:
			try:
				person.send(packet)
			except:
				continue
				#self.close_client(item,self.ClientDict[item].address

	def parse_input(self,client,packet):
		parser = Parser()
		parser.breakdown(packet)
		if parser.code == utils.codes["send_msg"] and parser.alias and parser.room: #sendmessage
			self.send_to_room(client,parser)
		elif parser.code == utils.codes["set_alias"]: #setalias
			self.set_alias(client,parser)
		elif parser.code == utils.codes["set_room"] and parser.alias: #setroom
			self.add_client_to_room(client,parser)
		elif parser.code == utils.codes["get_roomlist"] and parser.alias:
			self.send_room_list(client,parser)
		else:
			print("Invalid packet")
			return
			#invalid packet: do nothing

	def handle_connection(self, client, address):
		#clientVariables = ClientVariables(self.set_alias(client,address), address, self.add_client_to_room(client,address))
		#self.ClientDict[client] = clientVariables
		try:
			client.settimeout(None)
			while True:
				packet = client.recv(self.buf_size)
				if packet:
					print("%s:%s >> %s" % (address[0],address[1],packet))
					self.parse_input(client,packet)
					#self.send_to_room(client, packet)
				else:
					raise Exception #error('Client disconnected')
		except Exception as e:
			print(e.message)
			self.close_client(client,address)
			return False

if __name__ == "__main__":
		server = Server()
		server.run()
