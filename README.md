raspHA
======

Home Automation with Raspberry Pi via GPIO ports (c) 2013 by Nicolas Knotzer

RaspHA is a light-weight home automation server for raspberry Pi based on flask (python web microframework).

It can be used to control device-groups, scenarios or programms via traditional command interfaces (e.g. vimar 14518 for the by-me bus system) connected to the GPIO-Ports of the raspberry Pi.

RaspHA is configured via a single json config file ("config.json"). 

RaspHA consits of:

* raspHA.py (main program): a web-based grafical user interface to turn off or on device-groups, scenarios or programms.
* wunderground_daemon.py (module): a daemon which can turn off or on device-groups, scenarios or programms based on current weather conditions (e.g. windspeed and temperature) from weather underground. Rules can be defined in the config file to react to weather conditions (e.g. wind_kph > 10 and temperature_c < 5). You must provide your own api key from weather underground and your location in the config file. The weather daemon can be automatically started from the main program (autostart = "yes" in the config file). The daemon can use a lcd-display to show current weather conditions. For more information how to hook up a lcd display check out: http://learn.adafruit.com/drive-a-16x2-lcd-directly-with-a-raspberry-pi/overview

2015-05-18: http-basic-auth added, username and password are configured via config.json. if password is empty, authentication is disabled. i suggest using ssl-tunneling/https (e.g. stunnel4) to prevent cleartext transmission of the password...
  
TODOS for further versions:
* security hardening: raspHA must run as root to access GPIO ports, uses python "eval" to evaluate rules for the weatherunderground module, so arbitrary code could be executed if it is included in the response from wunderground! if you don't want to risk this do not enable the weather module...
* further modules (e.g. time-based control of devices)...
* control of modules (i.e. daemons) via the web-gui (start/restart/stop daemons)
 
