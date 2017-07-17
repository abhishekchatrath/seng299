class Parser():
	type = None
	room = None
	alias = None
	date = None
	#No checksum because we trust pythons TCP
	body = None

	def __init__(self):
		self.type = 0
		self.room = "0"
		self.alias = "0"
		self.date = "9/11"
		#No checksum because we trust pythons TCP
		self.body = "Lorem Ipsum"
	
	def breakdown(self, packet):
		packetT = packet.split("\\")
		self.type = packetT[0]
		self.room = packetT[1]
		self.alias = packetT[2]
		self.date = packetT[3]
		self.body = packetT[4]
		
		#Check Integrity
		
		
	def assemble(self, type, room, alias, date, body):
		
		packet = str(type) + "\\" + room + "\\" + alias + "\\" + date + "\\" + body
		
		return packet
		
		
		
		
	def type_get(self):
		return int(self.type)
		
	def room_get(self):
		return self.room
		
	def alias_get(self):
		return self.alias
	
	def date_get(self):
		return self.date
		
	def body_get(self):
		return self.body
	
