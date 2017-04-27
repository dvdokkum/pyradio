import os
import sys
import time
import threading
import subprocess

# parsing NPR feed
import feedparser
from urlparse import urlparse

## buttons
import RPi.GPIO as GPIO

## lcd
import lcd_init
from lcd_init import lcd as lcd

## setup buttons
GPIO.setmode(GPIO.BCM)

GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#some init values for the stream
stream = 0
stream_status = "off"

## available stations ##
stations = {}
stations['WXYC\n89.3 Chapel Hill'] = "http://audio-mp3.ibiblio.org:8000/wxyc.mp3"
stations['WFMU\n91.1 Jersey City'] = "http://stream0.wfmu.org/freeform-128k.mp3"
stations['Resonance\n104.4 London'] = "http://54.77.136.103:8000/resonance"
stations['WBUR\n90.9 Boston'] = "http://wbur-sc.streamguys.com/wbur"

news = {}

## todo, increment this every time a play happens
def next():
	z = len(stations)
	z = z - 1
	if stream_status == z:
		return 0
	elif type(stream_status) == int:
		r = stream_status
		r = r + 1
		return r
	else:
		return 0

def init_npr():
	global news
	#fetch rss feed
	d = feedparser.parse('https://www.npr.org/rss/podcast.php?id=500005')

	#parse url of mp3 file
	raw_url = d.entries[0].enclosures[0].url

	#mpg123 won't load https and doesn't handle query params well, so this cleans up the url
	o = urlparse(raw_url)
	clean_url = "http://" + o.netloc + o.path

	#grab the stream title incase we need it later
	npr_title = d.entries[0].title
	npr_title = npr_title.replace(": ","\n")

	news['npr'] = [npr_title, clean_url]

#display and plays stream, pass number of station in station dict
def play(n):
	global stream
	global stream_status
	
	# set the display and url values
	name = stations.keys()[n]
	url = stations.values()[n]

	off()
	
	lcd.message(name)

	stream = subprocess.Popen(["mpg123", "-q", url], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
	stream_status = n

def play_news():
	global stream
	global stream_status
	
	#save what was just playing so we can play it again when the news ends
	last = stream_status
	
	#fetches latest newscast
	init_npr()
	
	#kill the stream
	off()

	#display most recent news hour title
	lcd.message(news['npr'][0])
	
	#play the news (note the k argument in mpg123 is # of frames to skip. 900 should get us past the preroll ad)
	stream = subprocess.Popen(["mpg123", "-q", "-k 900", news['npr'][1]], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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

#turns everything off
def off():
	global stream_status
	lcd.clear()
	try:
		stream.kill()
	except (AttributeError, OSError):
		stream_status = "off"
		pass
	else:
		stream_status = "off"

def test():
	play(0)
	time.sleep(10)
	news_break()
	time.sleep(8)
	play(2)
	time.sleep(5)
	off()
	time.sleep(2)

def main():
	while True:
		s = GPIO.input(4)
		n = GPIO.input(17)

		if s == False:
			play(next())
			time.sleep(0.5)

		if n == False:
			news_break()
			time.sleep(0.5)

if __name__ == '__main__':
	sys.exit(main())