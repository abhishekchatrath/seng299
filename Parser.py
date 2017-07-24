class Parser():
	code = None
	room = None
	alias = None
	date = None
	body = None

	def __init__(self):
		self.code = None
		self.room = None
		self.alias = None
		self.date = None
		self.body = None

	def breakdown(self, packet):
		packetT = packet.split("\\")
		self.code = packetT[0]
		self.alias = packetT[1]
		self.room = packetT[2]
		self.date = packetT[3]
		self.body = packetT[4]

	def assemble(self, code, alias, room, date, body):
		packet = str(code) + "\\" + alias + "\\" + room + "\\" + date + "\\" + body
		return packet
