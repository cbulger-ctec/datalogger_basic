from time import sleep
import os
import threading
from thread import *
import subprocess
import logging

class watchdog (threading.Thread):
	def __init__(self,interval):
		super(watchdog, self).__init__() #Thread.__init__
		self.interval = interval
		
	def run(self):
		while (self.interval > 0):
			if (self.interval > 99.9):
				watchdog = 'f999'
			else:
				watchdog = 'f{:3.0f}'.format(self.interval*10)
			wd = os.open("/dev/watchdog", os.O_RDWR|os.O_SYNC)
			os.write(wd,watchdog)
			os.close(wd)
			sleep(1)
			self.interval -= 1
		return

	def stop(self):
		self.interval=0
		#feed watchdog with "3" to disable 
		wd = os.open("/dev/watchdog", os.O_RDWR|os.O_SYNC)
		os.write(wd,"3")
		os.close(wd)
