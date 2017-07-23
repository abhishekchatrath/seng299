import utils

class ChatRoom():

	room_name = None
	clientList = None
	messageList = None

	def __init__(self, name):
		self.room_name = name
		self.clientList = []
		self.messageList = []

	def set_room_name(self, name):
		if utils.validate_str(name):
			self.room_name = name

	def add_client(self, client):
		if client == None or len(self.clientList) >= utils.MAX_CLIENTS:
			return False
		self.clientList.append(client)

	def remove_client(self, client):
		if client == None or len(self.clientList) < 0:
			return False
		self.clientList.remove(client)

	def add_message(self, client, msg):
	 	if msg == None or client == None:
	 		return False
		if len(messageList) == utils.MAX_ROOM_MESSAGES:
			messageList = messageList[1:]
		messageList.append(msg)

	def get_messages(self):
		return messageList
