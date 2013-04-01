#!/usr/bin/env python

# Copyright (c) 2013 Nicolas Knotzer (nknotzer@gmail.com)
#
#    This file is part of raspHA
#
#    raspHA is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import RPi.GPIO as GPIO
import json
import sys
import os
import time
import requests
import logging
from daemon import Daemon
from Adafruit_CharLCD import Adafruit_CharLCD

logfile = "/var/log/raspHA_wunderground.log"
pidfile = "/var/run/raspHA_wunderground.pid"
configfile = "./config.json"

def loadconfig():
	""" parse config-file "config.json", store in dictionary variable "config" """
	global mod_config
	logging.info('app UID: '+str(os.geteuid())+' / app GID: '+str(os.getegid()))
	try:
		with open(configfile) as config_file:    
			config = json.load(config_file)
	except IOError as e:
		logging.error ("Can not open file \""+configfile+"\". I/O error({0}): {1}".format(e.errno, e.strerror))
		sys.exit (1)
		
	GPIO.setmode(eval(config["GPIO"]["setmode"]))
	for pin in config["GPIO"]["pins"]:
		GPIO.setup(int(pin["number"]),eval(pin["mode"]))
		GPIO.output(int(pin["number"]),eval(pin["initial"]))
		logging.info(pin["number"].zfill(2)+" "+pin["mode"]+" "+pin["initial"])
	
	for mod in config["modules"]:
	 	if mod["name"] == "Weather Underground":
			mod_config = mod
			logging.info(mod_config)
			break
	
def loadcurrentconditions():
	""" load current condition from weather underground """
	global conditions
	apiurl = "http://api.wunderground.com/api/" + mod_config["apikey"]  + "/conditions/q/" + mod_config["location"] + ".json"
	logging.info (apiurl)
	r = requests.get(apiurl)
	conditions = json.loads(r.text)
	logging.info (conditions)
	
	
def evaluaterules():
	""" evaluate rules defined in configfile """
	for key in conditions["current_observation"].keys():
		exec(key + " = conditions[\"current_observation\"]['" + key + "']")
	
	for rule in mod_config["rules"]:
		expr = rule["expression"]
		if (eval(expr) == True):
			logging.info (expr + ": TRUE")
			GPIO.output(int(rule["number"]), eval(rule["state"]))
		else:
			logging.info (expr + ": FALSE")
			
def lcd_showcurrentconditions():
	ignore = mod_config["lcd_ignore"].split(",")
	for cond in conditions["current_observation"]:
		cond_ignore = False;
		for i in ignore:
			if i in cond:
				cond_ignore = True
				break
				
		if (cond_ignore == False):
			if (cond == "observation_location" or cond == "display_location"):
				lcd.clear()
				lcd.message (str(cond))
				lcd.message ("\n")
				lcd.message (str(conditions["current_observation"][cond]["city"]))
			else:			
				lcd.clear()
				lcd.message (str(cond))
				lcd.message ("\n")
				lcd.message (str(conditions["current_observation"][cond]))
			time.sleep (float(mod_config["lcd_duration"]))
			
class wundergroundDaemon(Daemon):
	def run(self):
		global lcd
		loadconfig()
		if (mod_config["lcd"] == "yes"):
			lcd = Adafruit_CharLCD()
			lcd.begin(16,1)
		while True:
			loadcurrentconditions()
			evaluaterules()
			timestamp = time.time()
			while (time.time() - timestamp < mod_config["interval"]):
				if (mod_config["lcd"] == "yes"):
					lcd_showcurrentconditions()
			

if __name__ == "__main__":
	daemon = wundergroundDaemon(pidfile)
	logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s %(message)s')
	
	if len(sys.argv) == 3:
		configfile = sys.argv[2]
	elif len(sys.argv) == 2:
	    configfile = os.path.abspath(configfile)
	else:
		print "usage: %s start|stop|restart|foreground [raspHAConfigFile]" % sys.argv[0]
		sys.exit(2)
		
	if 'start' == sys.argv[1]:
		logging.info ("Starting daemon...")
		daemon.start()
	elif 'stop' == sys.argv[1]:
		daemon.stop()
		logging.info ("Daemon stopped")
	elif 'restart' == sys.argv[1]:
		daemon.restart()
	elif 'foreground' == sys.argv[1]:
		logging.info ("Starting daemon in foreground...")
		daemon.run()
	else:
		print "Unknown command"
		sys.exit(2)
	sys.exit(0)
	
