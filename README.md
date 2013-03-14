raspHA
======

Home Automation with Raspberry Pi via GPIO ports (c) 2013 by Nicolas Knotzer

RaspHA is a light-weight home automation server for raspberry Pi based on flask (python web microframework).

It can be used to control device-groups, scenarios or programms via traditional command interfaces (e.g. vimar 14518 for the by-me bus system) connected to the GPIO-Ports of the raspberry Pi.

RaspHA is configured via a single json config file ("config.json"). 

RaspHA consits of:

* raspHA.py (main program): a web-based grafical user interface to turn off or on device-groups, scenarios or programms.
* wunderground_daemon.py (module): a daemon which can turn off or on device-groups, scenarios or programms based on current weather conditions (e.g. windspeed and temperature) from weather underground. Rules can be defined in the config file to react to weather conditions (e.g. wind_kph > 10 and temperature_c < 5). You must provide your own api key from weather underground and your location in the config file. The weather daemon can be automatically started from the main program (autostart = "yes" in the config file)
  
TODOS for further versions:
* integrate authentication (i use OpenVPN for access to my lan, so i don't need authentication NOW)
* security hardening: raspHA must run as root to access GPIO ports, uses python "eval" to evaluate rules for the weather module, so arbitrary code could be executed, never trust user input ;-) 
* further modules (e.g. time-based control of devices)...
* control of modules (i.e. daemons) via the web-gui (start/restart/stop daemons)
 
