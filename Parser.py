class Parser():
	code = None
	room = None
	alias = None
	date = None
	#No checksum because we trust pythons TCP
	body = None

	def __init__(self):
		self.code = None
		self.room = None
		self.alias = None
		self.date = None
		#No checksum because we trust pythons TCP
		self.body = None

	def breakdown(self, packet):
		packetT = packet.split("\\")
		self.code = packetT[0]
		self.alias = packetT[1]
		self.room = packetT[2]
		self.date = packetT[3]
		self.body = packetT[4]

		#Check Integrity

	def assemble(self, code, alias, room, date, body):
		packet = str(code) + "\\" + alias + "\\" + room + "\\" + date + "\\" + body
		return packet

	def code_get(self):
		return int(self.code)

	def room_get(self):
		return self.room

	def alias_get(self):
		return self.alias

	def date_get(self):
		return self.date

	def body_get(self):
		return self.body
