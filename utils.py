socket = {
	'HOST' = ''
	'PORT' = 9000
}

BUFF_SIZE = 1024

commands = [
	'create_room',
	'name_room',
	'del_room',
	'toggle_block'
]

#todo check for special characters too
def validate_str(str):
	return isinstance(str, basestring) and (len(str) < 20) and (not ' ' in str)

def validate_cmd(cmd):
	return validate_str(cmd) and (cmd in commands)