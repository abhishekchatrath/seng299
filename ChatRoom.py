from DBWriter import DBWriter

class ChatRoom():

	room_name = None
	clientList = None
	db = None

	def __init__(self, name):
		self.room_name = name
		self.clientList = []
		#self.db = DBWriter() #todo check parameters after making DBWriter class

	def set_room_name(self, name):
		self.room_name = name #todo check if name is valid

	def add_client(self, client):
		if client == None or len(self.clientList) >= 20:
			return False
		self.clientList.append(client)

	def remove_client(self, client):
		if client == None or len(self.clientList) < 0:
			return False
		self.clientList.remove(client)

	# #def add_message(self, client, msg):
	# 	if msg == None or client == None:
	# 		return False
	# 	db.add_message(client, msg)
	#
	# #def get_messages(self):
	# 	#todo check if 10+ messages left in history?
	# 	return db.get_messages()
