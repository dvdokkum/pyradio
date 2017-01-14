import os
import sys
import time
import subprocess

stream = 0

#available streams, put these in a dict
wxyc = "http://audio-mp3.ibiblio.org:8000/wxyc.mp3"
wfmu = "http://stream0.wfmu.org/freeform-128k.mp3"

def main():
	play(wxyc)
	time.sleep(5)
	off()
	play(wfmu)
	time.sleep(5)
	off()

def play(s):
	global stream
	stream = subprocess.Popen(["mpg123", s], stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=False)

def off():
	stream.kill()

if __name__ == '__main__':
	sys.exit(main())