from time import sleep
import os
import threading
from thread import *
import subprocess
import logging

#Thread safe class for access the TS Hardware Control
#
#Class TsHardware
#
#Public Methods:
#	sd200_on(relay)
#	sd200_off(relay)

class TsHardware(threading.Thread, object):
	SD200 = "1_16";

	adc = {};

	ADC = {"LRADC_ADC1_millivolts":1, "LRADC_ADC2_millivolts":2, "LRADC_ADC3_millivolts":3, "LRADC_ADC4_millivolts":4};

	def __init__(self):
		super(TsHardware, self).__init__() 
		self.lock = threading.Lock();

	#set relay address (1-16)
	def sd200_on(self):
		self.lock.acquire()
		args = "--setdio=" + self.SD200
		subprocess.call(["tshwctl", args])
		self.lock.release();

	def sd200_off(self):
		self.lock.acquire()
		args = "--clrdio=" + self.SD200
		subprocess.call(["tshwctl", args])
		self.lock.release();

	def read_adc(self,channel):
		tmp=[];
		self.lock.acquire();
		p = subprocess.Popen(["tshwctl", "--cpuadc"],stdout=subprocess.PIPE, bufsize=1)
		self.lock.release();
		tmp = p.stdout.read()
		tmp = tmp.split("\n")
		for line in tmp:
			if len(line) > 0:
				val=line.split("=")
				if (val[0] in self.ADC):
					self.adc[self.ADC[val[0]]]=int(val[1])
		return self.adc[channel]
	

	def set_system_time_from_ZDA(self, zda):
		#parse NMEA ZDA string
		tmp=zda.split(",");
		nmea_type=tmp[0]
		if (nmea_type == "$GPZDA"):
			time_str=tmp[1];
			day=tmp[2];
			month=tmp[3];
			year=tmp[4];

		#TOD0: need to set system time
		#subprocess.call(["date", args])

	def get_short_mac_address(self):
		args = "--getmac";
		p = subprocess.Popen(["tshwctl", args],stdout=subprocess.PIPE, bufsize=1);
		tmp = p.stdout.read()
		tmp = tmp.split("\n")
		val = tmp[1].split("=")
		return val[1]
		
#	def close(self):
