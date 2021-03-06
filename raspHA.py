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
import time
import json
import os
import sys
import logging
from flask import Flask, render_template, request, Response
from subprocess import call
from functools import wraps

app = Flask(__name__)
logfile = "/var/log/raspHA.log"
configfile = "/opt/raspHA/config.json"

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == config["general"]["username"] and password == config["general"]["password"]
    
def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
		if config["general"]["password"] != "":
			auth = request.authorization
			if not auth or not check_auth(auth.username, auth.password):
				return authenticate()
		return f(*args, **kwargs)
    return decorated

def loadconfig():
	""" parse config-file, store in dictionary variable "config" """
	global config
	logging.info('app UID: '+str(os.geteuid())+' / app GID: '+str(os.getegid()))
	try:
		with open(configfile) as config_file:    
			config = json.load(config_file)
	except IOError as e:
		logging.error ("Can not open file \""+configfile+"\". I/O error({0}): {1}".format(e.errno, e.strerror))
		sys.exit (1)
	
def initgpio():
	""" initialize GPIO pins according to config file """
	global config
	logging.info(config["GPIO"]["setmode"])
	GPIO.setmode(eval(config["GPIO"]["setmode"]))
	
	for pin in config["GPIO"]["pins"]:
		GPIO.setup(int(pin["number"]),eval(pin["mode"]))
		GPIO.output(int(pin["number"]),eval(pin["initial"]))
		logging.info(pin["number"].zfill(2)+" "+pin["mode"]+" "+pin["initial"])

def loadmodules():
	""" load modules with autostart == yes """
	for mod in config["modules"]:
	 	if mod["autostart"] == "yes":
			call([mod["filename"],"restart",os.path.abspath(configfile)])
			logging.info ("started: "+mod["name"])
		
def gpiogetstate():
	""" read state of GPIO pins and write into dictionary variable "config" """		
	for pin in config["GPIO"]["pins"]:
		state = GPIO.input(eval(pin["number"]))
		pin[unicode("state")] = "GPIO.HIGH" if state else "GPIO.LOW" 
		logging.info(pin["number"].zfill(2)+" "+pin["mode"]+" "+pin["state"])	

@app.route("/")
@requires_auth
def main():
	""" show state of devices """
	gpiogetstate()		
	templateData = {
		'pins' : config["GPIO"]["pins"]
	}
	return render_template("main.html", **templateData)
	
@app.route("/<PinToChange>/<action>")
@requires_auth
def action(PinToChange, action):
	""" change status of devices """
	for pin in config["GPIO"]["pins"]:
		if pin["number"] == PinToChange:
			devicename = pin["name"]
			break
	
	if action == "on":
		GPIO.output(int(PinToChange), GPIO.HIGH)
		message = "\"" + devicename + "\" eingeschaltet."
	if action == "off":
		GPIO.output(int(PinToChange), GPIO.LOW)
		message = "\"" + devicename + "\" ausgeschaltet."
	if action == "trigger":
		GPIO.output(int(PinToChange), GPIO.HIGH)
		time.sleep (0.1)
		GPIO.output(int(PinToChange), GPIO.LOW)
		message = "\"" + devicename + "\" geschaltet."
	
	gpiogetstate()		
	templateData = {
		"pins" : config["GPIO"]["pins"],
		"message" : message,
	}
	return render_template("main.html", **templateData)

if __name__ == "__main__":
	logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s %(message)s')
	loadconfig()
	initgpio()
	loadmodules()
	app.run(host=config["general"]["host"], port=int(config["general"]["port"]), debug=config["general"]["debug"])
	

