#!/usr/bin/python
import serial
import os
from thread import *
from datetime import datetime
import time
import zlib, base64
from sys import getsizeof
from ConfigParser import ConfigParser
import threading
from TsHardware import TsHardware
import watchdog
from subprocess import call,PIPE,Popen

def write_data_log( directory, filename, data):
	fname = directory + "/" + filename
	try:
		reader = open(fname,'a+')
	except:
		reader = 0

	if reader:
		reader.write(data)
		reader.flush()
		os.fsync(reader.fileno())
		reader.close()

class readerThread (threading.Thread):
	def __init__(self,reader,interval,start,sensorname):
		super(readerThread, self).__init__() #Thread.__init__
		self.reader = reader
		self.interval = interval
		self.starttime = start
		self.data = ""
		self.sensorname = sensorname
		#self.reader.flushInput()

	def run(self):
		duration = (datetime.now()-self.starttime).total_seconds()
		while (duration < self.interval):
			duration = (datetime.now()-self.starttime).total_seconds()
			try:
				self.data = self.data + '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) + self.reader.readline()+ "\n"
			except:
				pass
			duration = (datetime.now()-self.starttime).total_seconds()

	def close(self):
		return self.data

settings = {}

config = ConfigParser()
config.read('config.conf')
for section in config.sections():
	if config.has_option(section, 'type') and config.get(section,'type')=='sensor':
		settings[section,'port'] = config.get(section,'port')
		settings[section,'baud'] = config.getint(section,'baud')
		settings[section,'timeout'] = config.getint(section,'timeout')
		settings[section,'parity'] = config.get(section,'parity')
		settings[section,'interval'] = config.getint(section,'interval')
		settings[section,'datadir'] = config.get(section,'datadir')
		settings[section,'datalogging'] = config.getint(section,'datalogging')
		settings[section,'reader'] = serial.Serial(settings[section,'port'],\
			settings[section,'baud'],\
			timeout=settings[section,'timeout'], \
			parity=settings[section,'parity'])
	elif section == 'MAIN':
		settings[section,'interval'] = config.getint(section,'interval')
		settings[section,'timeout'] = config.get(section,'timeout')

#connect to nupoint modem
ts = TsHardware()


#wd = watchdog.watchdog(settings['MAIN','timeout'])
#wd.start()




start = datetime.now()
computer_id = ts.get_short_mac_address()
t_end = time.time();
t_wkup = int(t_end) - (int(t_end)%settings['MAIN','interval']) + settings['MAIN','interval']
for section in config.sections():
	if config.has_option(section, 'type') and config.get(section,'type')=='sensor':
		settings[section,'data'] = ""
		settings[section,'thread'] = readerThread(settings[section,'reader'],\
			settings[section,'interval'], start, section)
		settings[section,'thread'].start()

date_str = datetime.fromtimestamp(time.time()).strftime('%y%m%d%H%M%S')

buffer = ""
for section in config.sections():
	if config.has_option(section, 'type') and config.get(section,'type')=='sensor':
		settings[section,'thread'].join()
		data = settings[section,'thread'].close()
		
		#write datafile
		if settings[section,'datalogging']:
			write_data_log(settings[section,'datadir'],section + "_" + date_str[0:6]+".log",data)

wakeup = t_wkup - time.time()

#check to see if anyone is logged on
p = Popen(["users"],stdout=PIPE, bufsize=1)
users = p.stdout.read()
users = users.strip()

if (len(users) == 0):
	if (wakeup > 0):
		t_cmd = "--timewkup=" + str(wakeup)
		call(["tshwctl", t_cmd, "--sleep"])
		#time.sleep(wakeup)
		#wd.stop()
else:
	print len(users)
	if (wakeup > 0):
		time.sleep(wakeup)
		Popen(["nohup", "/home/user/datalogger/datalogger.py"])
