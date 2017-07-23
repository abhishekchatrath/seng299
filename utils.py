socket = {
	'HOST': '',
	'PORT': 9000,
}

codes = {
	'send_msg': '1',
	'set_alias': '2',
	'set_room': '3',
	'get_roomlist' : '4',
	'recv_msg': '5',
	'recv_roomlist': '6',
	'alias_success': '7',
	'room_success' : '8',
	'alias_invalid': '9',
	'room_invalid' : '10',
}

BUFF_SIZE = 1024
MAX_CLIENTS = 20
MAX_ROOMS = 10
MIN_ROOMS = 1
GEN_ROOM = 'General'
DATE_FORMAT = "%Y-%m-%d %H:%M"
DATE_FORMAT = "%H:%M"
MAX_ROOM_MESSAGES = 10

commands = [
	'create_room',
	'rename_room',
	'del_room',
	'toggle_block'
]

def validate_str(str):
	return isinstance(str, basestring) and (len(str) <= 20) and (not '\\' in str) and (not ' ' in str)

def validate_cmd(cmd):
	return validate_str(cmd) and (cmd in commands)
