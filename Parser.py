#breaks down and assembles packets that are sent between Clients and the Server
import utils

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

	def pad(self,packet):
		# if len(packet) < int(utils.BUFF_SIZE)/2 + 10:
		# 	num_spaces = int(utils.BUFF_SIZE)/2 + 100 - len(packet)
		# 	packet += '\\' + ' '*num_spaces
		if len(packet) < int(utils.BUFF_SIZE):
			num_spaces = int(utils.BUFF_SIZE) - len(packet)
			packet += '\\' + ' '*(num_spaces-1)
		return packet
