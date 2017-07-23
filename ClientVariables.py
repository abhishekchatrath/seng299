class ClientVariables(object):
	alias = None
	address = None
	chatroom = None
	
	def __init__(self,alias,address,chatroom):
		self.alias = alias
		self.address = address
		self.chatroom = chatroom
	
	def __str__(self):
		return "%s\t%s\t%s\t%s" % (self.alias, self.address[0], self.address[1], self.chatroom)
