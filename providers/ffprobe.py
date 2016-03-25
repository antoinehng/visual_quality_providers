import os
import subprocess
import json

from dependencies import FFPROBE_BIN


class media_info():

	def __init__(self, file_path):
		self.file_path = file_path
		self.filename = os.path.basename(file_path)

		cmd = FFPROBE_BIN
		opts = [
			'-hide_banner ',
			'-loglevel ', 'quiet ',
			'-print_format ', 'json ',
			'-pretty ',
			'-show_format ',
			'-show_streams ',
			'-show_error ',
			'-i ', file_path
			]

		p = subprocess.Popen([cmd, opts], stdout=subprocess.PIPE)
		probe_data = json.loads(p.communicate()[0])

		self.error = probe_data.get("error", None)
		if self.error != None :
			self.error = str(self.error["code"])+" : "+self.error["string"]

		elif probe_data.get("streams", None) != None :
			for stream in probe_data["streams"]:
				if stream.get("codec_type", None) == "video":
					self.aspect_ratio = stream.get("display_aspect_ratio", "undefined")
					self.bitdepth = stream.get("bits_per_raw_sample", "undefined")
					self.bitrate = stream.get("bit_rate", "undefined")
					self.codec = stream.get("codec_long_name")
					self.colorspace = stream.get("color_space", "undefined")
					self.duration = stream.get("duration")
					self.framerate = stream.get("r_frame_rate").replace("/1","")
					self.height = stream.get("height")
					self.level = stream.get("level", "undefined")
					self.pixel_aspect_ratio = stream.get("sample_aspect_ratio")
					self.pixel_format = stream.get("pix_fmt", "undefined")
					self.profile = stream.get("profile", "undefined")
					self.width = stream.get("width")
				else:	
					# do not care about audio for now
					pass

		else:
				self.error ="Unknown ffprobe error"
