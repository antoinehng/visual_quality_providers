import os

if os.name == 'nt':
	FFPROBE_BIN = os.path.join( os.path.dirname(os.path.abspath(__file__)), "win", "ffprobe.exe")
	FFMPEG_BIN = os.path.join( os.path.dirname(os.path.abspath(__file__)), "win", "ffmpeg.exe")
else:
	# Not tested for now
	FFPROBE_BIN = os.path.join( os.path.dirname(os.path.abspath(__file__)), "unix", "ffprobe")
	FFMPEG_BIN = os.path.join( os.path.dirname(os.path.abspath(__file__)), "unix", "ffmpeg")