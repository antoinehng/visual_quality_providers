def tc2s(timecode):
	h = int(timecode.split(':')[0])
	m = int(timecode.split(':')[1])
	s = int(timecode.split(':')[2].split('.')[0])
	return s + ( 60 * ( m + 60 * h ) ) 

def error(message):
	print "[ERROR] "+message

def update_state(state, message=None):
	if message != None :
		print "["+state.upper()+"] "+message
	else:
		print "["+state.upper()+"]"
