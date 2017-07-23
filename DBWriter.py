#import MySQLdb

class DBWriter():

	cursor = None
	table_name = None

	def __init__(self):
		db = MySQLdb.connect(host = "localhost", user = "root", passwd = "mysqlpassword")
		self.cursor = db.cursor()

	def create_room_table(self, table_name):
		self.cursor.execute("CREATE DATABASE %s" % (table_name))#todo: define table columns
		self.table_name = table_name

	def delete_room_table(self):
		self.cursor.execute("DROP DATABASE %s" % (self.table_name))
		self.table_name = ""

	def set_table_name(self, table_name):
		self.cursor.execute("RENAME TABLE %s to %s" % (self.table_name, table_name))
		self.table_name = table_name

	def add_message(self, client, time, msg):
		self.cursor.execute()

	def get_messages(self):
		return

if __name__ == "__main__":
	print('Starting Database connection...')
	db = DBWriter()
	print('Connected to database. Connection details...\nHOST: localhost\nPORT: 3306\nUSER: root\nPASSWD: mysqlpassword\n')

	print('Creating table test_table_1...')
	db.create_room_table("test_table_1")
	print('Created table %s\n' % (db.table_name))

	"""
	print('Renaming table %s to test_table_2' % (db.table_name))
	db.set_table_name("test_table_2")
	print('Renamed table to %s\n' % (db.table_name))
	"""
	print('Deleting table %s...' % (db.table_name))
	db.delete_room_table()
	print('Deleted table.\n')
