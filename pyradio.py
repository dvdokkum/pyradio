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
	stream_status = s

def play_news():
	global stream
	global stream_status
	
	#save what was just playing so we can play it again when the news ends
	last = stream_status
	
	#fetches latest newscast
	init_npr()
	
	#kill the stream
	off()
	
	#play the news (note the k argument in mpg123 is # of frames to skip. 900 should get us past the preroll ad)
	stream = subprocess.Popen(["mpg123", "-q", "-k 12000", station['npr']], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
	stream_status = "news"
	stream.wait()

	# if the news has ended, continue playing last station
	if stream_status == "news":
		if last == "news" or last == "off":
			pass
		else:
			play(last)	

#play news in a thread so we can queue and interrupt if necessary
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
	play(station['wfmu'])
	time.sleep(10)
	news_break()
	time.sleep(8)
	play(station['wxyc'])
	time.sleep(5)
	off()

if __name__ == '__main__':
	sys.exit(main())