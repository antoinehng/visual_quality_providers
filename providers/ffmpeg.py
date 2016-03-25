from __future__ import division
import sys, os, time
import subprocess
import xml, json

from providers import helpers
from providers import ffprobe
from dependencies import FFMPEG_BIN


class ffmpeg():

	supported_metrics = ['psnr','ssim']

	def process(self, reference_path, compressed_path, metric):
		
		helpers.update_state("queued", metric.upper()+' task')
		
		self.metric = metric.lower()
		if self.metric in self.supported_metrics:

			if self.pre_task(reference_path, compressed_path) == True:
				if self.task(self.reference, self.compressed, metric) == True:
					if self.acknowledge() == True:
						self.post_task()

		else:
			helpers.error('Metric not supported: '+ metric.upper())
			

	def pre_task(self, reference_path, compressed_path):

		helpers.update_state("probing", reference_path)
		self.reference = ffprobe.media_info(reference_path)
		if getattr(self.reference, 'error', None) != None:
			helpers.error(self.reference.error)
			return False
		
		helpers.update_state("probing", compressed_path)
		self.compressed = ffprobe.media_info(compressed_path)
		if getattr(self.compressed, 'error', None) != None:
			helpers.error(self.compressed.error)
			return False

		return True


	def task(self, reference, compressed, metric):

		self.workingdir=os.path.join( os.path.dirname(os.path.abspath(__file__)), "measures")
		self.raw_datafile_basename =  self.compressed.filename+'.'+self.metric+'.ffmpeg.temp'
		self.raw_datafile=os.path.join(self.workingdir, self.raw_datafile_basename)

		cmd = FFMPEG_BIN
		opts = [
			' -hide_banner ',
			' -i ', compressed.file_path,
			' -i ', reference.file_path,
			' -lavfi ', '[0]scale='+str(reference.width)+':'+str(reference.height)+'[scaled];[scaled][1]'+self.metric+'=stats_file=\"'+self.raw_datafile_basename+'\"',
			' -f ', ' null ',
			' - '
			]
		self.process = subprocess.Popen([cmd, opts], cwd=self.workingdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
		helpers.update_state("starting")
		return True


	def acknowledge(self):
		
		nb_frames = helpers.tc2s(self.reference.duration)*(int(self.reference.framerate))
		last_progress = -1
		start_time = time.time()

		while True:

			if self.process.poll() is not None:
				helpers.update_state("processing", '100%')
				return True

			else:
				line = self.process.stdout.readline()
				if "time=" in line:

					frame = int(line[line.find('frame=')+6:line.find('fps=')].strip())
					progress = int((frame/nb_frames)*100)

					if progress > last_progress:
						helpers.update_state("processing", str(progress)+'%')
						last_progress = progress

						current_time = time.time()
						elapsed_time = current_time - start_time
						if progress > 0:
							estimated_task_duration = round((100*elapsed_time)/progress)
							estimated_end_time = start_time + estimated_task_duration
							print 'Task will end at : '+time.asctime(time.localtime(estimated_end_time))

					time.sleep(.5) # ffmpeg usually appends new line every 500ms


	def post_task(self):
		print 'Compiling data...'

		data={}
		data['date']= time.strftime("%Y/%m/%d %H:%M:%S")
		
		data['reference_file']={}
		for attr, value in self.reference.__dict__.iteritems():
			data['reference_file'][attr]=value

		data['compressed_file']={}
		for attr, value in self.compressed.__dict__.iteritems():
			data['compressed_file'][attr]=value

		data['measures']={}
		data['measures']['metric']=self.metric

		data['measures']['frames']=[]
		data['measures']['average']=0

		with open(self.raw_datafile) as f:
			for line in f:
				value = {}

				if self.metric == 'ssim':
					value['index'] = line[line.find('n:')+2:line.find('Y:')].strip()
					value['ssim']={}
					value['ssim']['y'] = line[line.find('Y:')+2:line.find('U:')].strip()
					value['ssim']['u'] = line[line.find('U:')+2:line.find('V:')].strip()
					value['ssim']['v'] = line[line.find('V:')+2:line.find('All:')].strip()
					value['ssim']['average'] = line[line.find('All:')+4:line.find('(')].strip()
					data['measures']['average']+=float(value['ssim']['average'])
					value['ssim']['decibel'] = line[line.find('(')+1:line.find(')')].strip()

				elif self.metric == 'psnr':
					value['index'] = line[line.find('n:')+2:line.find('mse_avg:')].strip()
					value['mse']={}
					value['mse']['average'] = line[line.find('mse_avg:')+8:line.find('mse_y:')].strip()
					value['mse']['y'] = line[line.find('mse_y:')+6:line.find('mse_u:')].strip()
					value['mse']['u'] = line[line.find('mse_u:')+6:line.find('mse_v:')].strip()
					value['mse']['v'] = line[line.find('mse_v:')+6:line.find('psnr_avg:')].strip()
					value['psnr']={}
					value['psnr']['average'] = line[line.find('psnr_avg:')+9:line.find('psnr_y:')].strip()
					value['psnr']['y'] = line[line.find('psnr_y:')+7:line.find('psnr_u:')].strip()
					value['psnr']['u'] = line[line.find('psnr_u:')+7:line.find('psnr_v:')].strip()
					value['psnr']['v'] = line[line.find('psnr_v:')+7:len(line)].strip()
					data['measures']['average']+=float(value['psnr']['average'])

				data['measures']['frames'].append(value)

			data['measures']['average']/=len(data['measures']['frames'])
			print self.metric.upper() +': '+ str(data['measures']['average'])

		print 'Dumping file...'		
		with open(os.path.join( os.path.dirname(os.path.abspath(__file__)), "measures", self.compressed.filename+"."+self.metric+".json" ), 'w') as f:
			json.dump(data, f)

		os.remove(self.raw_datafile)

		helpers.update_state("finished")
