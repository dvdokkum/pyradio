#!/usr/bin/python

import lcd_init
from subprocess import *
from time import sleep, strftime
from datetime import datetime

lcd = lcd_init.lcd

cmd = "ip addr show wlan0 | grep inet | awk 'FNR == 1 {print $2}' | cut -d/ -f1"

def run_cmd(cmd):
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.communicate()[0]
        return output

while 1:
        lcd.clear()
        ipaddr = run_cmd(cmd)
        lcd.message(datetime.now().strftime('%b %d  %H:%M:%S\n'))
        lcd.message('IP %s' % ( ipaddr ) )
        sleep(2)