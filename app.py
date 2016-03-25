import sys, getopt
from providers.ffmpeg import ffmpeg

reference_file = raw_input("Reference video file path : ")
compressed_file = raw_input("Compressed video file path : ")
metric = raw_input("Choose metric [ssim, psnr] : ")

provider = ffmpeg()
provider.process(reference_file, compressed_file, metric)