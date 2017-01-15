import os
import sys
import time
import subprocess

import feedparser
from urlparse import urlparse

stream = 0

## available stations ##
station = {}
station['wxyc'] = "http://audio-mp3.ibiblio.org:8000/wxyc.mp3"
station['wfmu'] = "http://stream0.wfmu.org/freeform-128k.mp3"

###########################
# get npr hourly newscast #
###########################

#fetch rss feed
d = feedparser.parse('https://www.npr.org/rss/podcast.php?id=500005')

#parse url of mp3 file
raw_url = d.entries[0].enclosures[0].url

#mpg123 won't load https and doesn't handle query params well, so this cleans up the url
o = urlparse(raw_url)
npr = "http://" + o.netloc + o.path

#grab the stream title incase we need it later
npr_title = d.entries[0].title

def play(s):
	off()
	global stream
	stream = subprocess.Popen(["mpg123", "-q", s], stdout=subprocess.PIPE, stdin=subprocess.PIPE)

### TODO: Figure out a way to both play something when this file ends AND interrupt it with a play command (threading???)
def play_news():
	off()
	global stream
	stream = subprocess.Popen(["mpg123", "-q", "-k 12000", npr], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
	while stream.poll() is None:
		continue
	else:
		print "the stream is dead"

def off():
	try:
		stream.kill()
	except (AttributeError, OSError):
		pass

def main():
	play(station['wxyc'])
	time.sleep(5)
	play_news()
	time.sleep(10)
	play(station['wfmu'])
	time.sleep(5)
	off()

if __name__ == '__main__':
	sys.exit(main())