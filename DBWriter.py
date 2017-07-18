"""
Just a placeholder class for storing and retrieving messages from a DB
"""

class DBWriter():
	
	table = None
	name = None
	
	def __init__(self):
		self.table = {} #not really
	
	def create_room_table(self):
		#is this even required when you have init?
	
	def delete_room_table(self):
		#is this even required when you can close an object?
	
	def set_table_name(self, name):
		self.name = name
	
	def add_message(self, client, time, msg):
		table[time] = (client, msg) #tuples are fun!
	
	def get_messages(self):
		return []
