import os
import sys
import time
import threading
import subprocess

import feedparser
from urlparse import urlparse

stream = 0
stream_status = "off"

## available stations ##
station = {}
station['wxyc'] = "http://audio-mp3.ibiblio.org:8000/wxyc.mp3"
station['wfmu'] = "http://stream0.wfmu.org/freeform-128k.mp3"

def init_npr():
	global station
	#fetch rss feed
	d = feedparser.parse('https://www.npr.org/rss/podcast.php?id=500005')

	#parse url of mp3 file
	raw_url = d.entries[0].enclosures[0].url

	#mpg123 won't load https and doesn't handle query params well, so this cleans up the url
	o = urlparse(raw_url)
	npr = "http://" + o.netloc + o.path
	station['npr'] = npr

	#grab the stream title incase we need it later
	npr_title = d.entries[0].title

def play(s):
	global stream
	global stream_status
	off()
	stream = subprocess.Popen(["mpg123", "-q", s], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
	stream_status = "stream"

def play_news():
	global stream
	global stream_status
	off()
	init_npr()
	stream = subprocess.Popen(["mpg123", "-q", "-k 12000", station['npr']], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
	stream_status = "news"
	stream.wait()
	if stream_status == "news":
		play(station['wxyc'])	

def news_break():
	t = threading.Thread(target=play_news)
	t.start()

def off():
	global stream_status
	try:
		stream.kill()
	except (AttributeError, OSError):
		stream_status = "off"
		pass
	else:
		stream_status = "off"

def main():
	play(station['wxyc'])
	time.sleep(5)
	news_break()
	time.sleep(15)
	play(station['wfmu'])
	time.sleep(5)
	off()

if __name__ == '__main__':
	sys.exit(main())