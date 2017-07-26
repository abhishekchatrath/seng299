import socket
import threading
import os
import utils
import time
import datetime
import logging

from Parser import Parser
from ChatRoom import ChatRoom
from ClientVariables import ClientVariables

class Server():
	host = None
	port = None
	sock = None
	buf_size = None
	ClientDict = {} #keys are client sockets, values are ClientVariables
	ChatroomDict = {} #keys are chatroom name, values are Chatroom objects
	BlockedList = [] #list of blocked IP's


	#intializes the server socket and creates the static chatroom General
	def __init__(self):
		self.host = utils.socket.get('HOST', '')
		self.host = ""
		self.port = utils.socket.get('PORT', 9000)
		self.buf_size = utils.BUFF_SIZE
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))
		self.ChatroomDict['General'] = ChatRoom(utils.GEN_ROOM)

	#Server listens for connections and starts a thread for each new client connection up to max 20
	def run(self):
		print('Starting Server.')
		self.sock.listen(5)
		print('Server is listening...')
		threading.Thread(target=self.handle_server_admin).start()
		while True:
			client, address = self.sock.accept()
			if address[0] in self.BlockedList:
				continue
			if len(self.ClientDict) < utils.MAX_CLIENTS:
				logging.info('Connection Received: %s' % str(address))
				clientVariables = ClientVariables("",address,"")
				self.ClientDict[client] = clientVariables
				threading.Thread(target=self.handle_connection, args=(client, address)).start()
			else:
				logging.info('Max Capacity reached')
				client.close()

	#listens for commands from the server admin
	def handle_server_admin(self):
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
					elif command == utils.commands[1]:#del_room
						self.delete_room()
					elif command == utils.commands[2]:#block
						self.block_client()
					elif command == utils.commands[3]:#unblock
						self.unblock_client()
				else:
					print("Invalid command. Please try again.")
			except Exception as e:
				logging.exception(e)
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
			except Exception as e:
				logging.exception(e)
				self.sock.close()
				os._exit(1)
		else:
			print("Sorry, the maximum room limit of %s has already been reached." % (utils.MAX_ROOMS))

	def delete_room(self):
		if len(self.ChatroomDict) > utils.MIN_ROOMS:
			try:
				roomlist = "Type the name of the room you want to delete:"
				for room in self.ChatroomDict.keys():
					roomlist += '\n' + room
				roomlist += '\n'
				print roomlist
				room_name = raw_input()
				if (room_name in self.ChatroomDict.keys()) and (room_name != utils.GEN_ROOM):
					client_list = self.ChatroomDict[room_name].clientList
					parser = Parser()
					packet = parser.assemble(utils.codes["leave_room"],"","","","")
					for client in client_list:
						client.send(packet)
						logging.info("Sent packet: %s" %(packet))
					del self.ChatroomDict[room_name]
					print('The room %s has been deleted.' % (room_name))
				else:
					print("Invalid room name entered. Command has been aborted.")
			except Exception as e:#for clean exit when user types CTRL+C
				logging.exception(e)
				self.sock.close()
				os._exit(1)
		else:
			print("Sorry, the minimum room limit has already been reached.")

	def block_client(self):
		clientInfo = ""
		for clientVars in self.ClientDict.values():
			clientInfo += clientVars.__str__() + "\n"
		print('Please type the IP you wish to block and press Enter.\n%s\n' % (clientInfo))
		ip = raw_input()
		isValid = False
		for clientVar in self.ClientDict.values():
			if clientVar.address[0] == ip:
				isValid = True
				break
		if isValid:
			self.BlockedList.append(ip)
			parser = Parser()
			packet = parser.assemble(utils.codes["quit_client"],"","","","")
			for client in self.ClientDict.keys():
				if (self.ClientDict[client].address[0]) == ip:
					client.send(packet)
					logging.info("Sent packet: %s" %(packet))
					self.close_client(client, self.ClientDict[client].address)
			print('%s has been blocked.' % (ip))
		else:
			print("%s is not an IP in the client list" %(ip))

	def unblock_client(self):
		clientInfo = ""
		for blockedIP in self.BlockedList:
			clientInfo += blockedIP + "\n"
		print('Please type the IP you wish to unblock and press Enter.\n%s\n' % (clientInfo))
		ip = raw_input()
		if ip in self.BlockedList:
			self.BlockedList.remove(ip)
			print('%s has been unblocked.' % (ip))
		else:
			print("%s is not in the blocked list." %(ip))

	#closes a client socket and removes that Client from the ClientDict and ChatroomDict
	def close_client(self,client,address):
		if client in self.ClientDict.keys():
			if self.ClientDict[client].chatroom:
				room = self.ClientDict[client].chatroom
				if room in self.ChatroomDict.keys():
					self.ChatroomDict[room].remove_client(client)
			del self.ClientDict[client]
			logging.info("Closed Client %s:%s" %(address[0],address[1]))
			client.close()

	def set_alias(self, client, parser):
		try:
			if utils.validate_str(parser.alias):
				for key in self.ClientDict:
					if self.ClientDict[key].alias == parser.alias:
						packet = parser.assemble(utils.codes["alias_invalid"],parser.alias,"","","")
						client.send(packet)
						logging.info("Sent packet %s" %(packet))
						return
				room_list = ""
				for room in self.ChatroomDict.keys():
					room_list += room + " "
				self.ClientDict[client].alias = parser.alias
				packet = parser.assemble(utils.codes["alias_success"],self.ClientDict[client].alias,"","",room_list)
				client.send(packet)
				logging.info("Sent packet %s" %(packet))
			else:
				packet = parser.assemble(utils.codes["alias_invalid"],parser.alias,"","","")
				client.send(packet)
				logging.info("Sent packet %s" %(packet))
		except:
			self.close_client(client,self.ClientDict[client].address)

	def add_client_to_room(self, client, parser):
		try:
			if parser.room in self.ChatroomDict.keys():
				self.ChatroomDict[parser.room].add_client(client)
				self.ClientDict[client].chatroom = parser.room
				packet = parser.assemble(utils.codes["room_success"],self.ClientDict[client].alias,self.ClientDict[client].chatroom,"","")
				client.send(packet)
				logging.info("Sent packet %s" %(packet))
				messagelist = self.ChatroomDict[parser.room].get_messages()
				for message in messagelist:
					message_packet = parser.assemble(utils.codes["recv_msg"],self.ClientDict[client].alias,self.ClientDict[client].chatroom,"",message)
					message_packet = parser.pad(message_packet)
					time.sleep(0.1)
					client.send(message_packet)
					logging.info("Sent packet %s" %(message_packet))
			else:
				packet = parser.assemble(utils.codes["room_invalid"],self.ClientDict[client].alias,parser.room,"","")
				client.send(packet)
				logging.info("Sent packet %s" %(packet))
		except:
			self.close_client(client,self.ClientDict[client].address)

	#sends a space-separated string that contains the list of room names currently available to the client
	def send_room_list(self,client,parser):
		self.ClientDict[client].chatroom = None
		if parser.room in self.ChatroomDict.keys():
			self.ChatroomDict[parser.room].remove_client(client)
		try:
			room_list = ""
			for room in self.ChatroomDict.keys():
				room_list += room + " "
			packet = parser.assemble(utils.codes["recv_roomlist"],self.ClientDict[client].alias,"","",room_list)
			client.send(packet)
			logging.info("Sent packet %s" %(packet))
		except:
			self.close_client(client,self.ClientDict[client].address)

	def send_to_room(self,client,parser):
		date = str(datetime.datetime.now().strftime(utils.DATE_FORMAT))
		formatted_message = date + " " + self.ClientDict[client].alias + ": " + parser.body
		packet = parser.assemble(utils.codes["recv_msg"],self.ClientDict[client].alias,self.ClientDict[client].chatroom,"",formatted_message)
		room = self.ClientDict[client].chatroom
		self.ChatroomDict[room].add_message(client,formatted_message)
		for person in self.ChatroomDict[room].clientList:
			try:
				person.send(packet)
				logging.info("Sent packet %s" %(packet))
			except:
				continue

	#determines what the content of the packet is
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
			logging.info("Recieved Invalid Packet %s" %(packet))
			return

	#recieves packets from the client and does the appropriate action with them
	def handle_connection(self, client, address):
		try:
			client.settimeout(None)
			while True:
				packet = client.recv(self.buf_size)
				if packet:
					logging.info("Recieved packet: %s" % (packet))
					self.parse_input(client,packet)
				else:
					raise Exception
		except Exception as e:
			logging.exception(e)
			self.close_client(client,address)
			return False

if __name__ == "__main__":
		logging.basicConfig(filename='Serverlog.log', format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S%p\t', level=logging.DEBUG,filemode='w')
		server = Server()
		server.run()
