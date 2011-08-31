#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# linstaller main executable - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#

import linstaller.core.main as m
import linstaller.core.config as config
import linstaller.core.modulehelper as mh
from linstaller.core.main import warn, info, verbose

import exceptions

import t9n.library
_ = t9n.library.translation_init("linstaller")

import os, sys

reboot = False

def launch_module(module, special):
	global reboot
	
	# Adjust cfg.module to read "module:<modulename>"
	cfg.module = "module:%s" % module.split(".")[0]
	
	# Load module...
	mod = mh.Module(module)
	modclass = mod.load(main_settings, modules_settings, cfg)
	
	# It is special? Add to executed_special.
	if module in special:
		executed_special.append(module)
	
	# Start module
	try:
		res = modclass.start()
	except exceptions.SystemExit:
		return "exit"
	except:
		# Something nasty happened.
		# We should revert any 'special' changes (mounts, etc).
		
		verbose("Something nasty happened. Reverting special changes.")
		
		executed_special.reverse() # Reverse.
		for modu in executed_special:
			verbose("Reverting %s" % modu)
			_revert = mh.Module(modu)
			_revertc = _revert.load(main_settings, modules_settings, cfg)
			
			# Revert
			_revertc.revert()
		
		# Now raise the original exception	
		print sys.exc_info()[0]
		raise
		
	# Update modules_settings
	if not module.split(".")[-1] == "inst":
		# Frontend. Add only the module name
		modules_settings[module.split(".")[0]] = modclass.return_settings()
	else:
		# .inst module. Add it anyway, but with ".inst"
		modules_settings[module] = modclass.return_settings()

	if res == "restart":
		# restart module.
		return launch_module(module, special)
	elif res == "kthxbye":
		# Reboot
		return "kthxbye"


## Welcome the linstaller :)
## This is the main executable, and should be called with something like this:
##  linstaller --config=<configuration> start
## where <configuration> should be a configuration file in /etc/linstaller (without path).
## if --config is omitted, will be used "default" by default.

verbose("started linstaller - version %s" % m.VERSION)

_action = False
_config = "default"
_frontend = "cli"

# Parse arguments
for arg in sys.argv:
	# Split = arguments
	arg = arg.split("=")
	if arg[0] in ("--config","-c"):
		# Require second argument
		if len(arg) < 2: raise m.UserError("--config requires an argument!")
		_config = arg[1]
	elif arg[0] in ("--frontend","-f"):
		# Require second argument
		if len(arg) < 2: raise m.UserError("--frontend requires an argument!")
		_frontend = arg[1]
	elif arg[0] == "help":
		_action = "help"
	elif arg[0] == "start":
		_action = "start"

if not _action:
	print _("You have to pass at least an action!")
	_action = "help"

if _action == "help":
	print _("SYNTAX: %s <options> [ACTION]") % sys.argv[0]
	print
	print _("Recognized options:")
	print _(" -c|--config		- Selects the configuration file to read")
	print _(" -f|--frontend		- Selects the frontend to use (def: cli)")
	print
	print _("Recognized actions:")
	print _(" help			- Displays this help message, then exits.")
	print _(" start			- Starts the installer.")
	sys.exit(0)
elif _action == "start":
	
	if not os.path.join(config.configpath, _config):
		raise m.UserError(_("%s does not exist! Adjust --config accordingly." % _config))
	else:
		verbose("Selected configuration file: %s" % _config)
	
	# Ohhh yay :) This action that will actually start the installer and its appropriate frontend.
	
	# Create target directory
	if not os.path.exists("/linstaller/target"):
		os.makedirs("/linstaller/target")
	
	# Load configuration file
	cfg = config.ConfigRead(_config, "linstaller")
	
	# Populate main_settings
	main_settings = {}
	main_settings["frontend"] = _frontend
	main_settings["distro"] = cfg.printv("distribution")
	main_settings["modules"] = cfg.printv("modules")
	main_settings["special"] = cfg.printv("special")
	
	verbose("Frontend: %s" % main_settings["frontend"])
	verbose("Distro: %s" % main_settings["distro"])
	verbose("Modules: %s" % main_settings["modules"])
	
	# Create modules_settings
	modules_settings = {}
	
	# 'special' modules executed
	executed_special = []
	
	# Begin loop modules...
	for module in main_settings["modules"].split(" "):
		if module:
			res = launch_module(module, main_settings["special"].split(" "))
			if res == "exit":
				break # Exit.
			elif res == "kthxbye":
				reboot = True # Reboot

	# Finished installation. Revert changes made to the system.
	executed_special.reverse() # Reverse.
	for modu in executed_special:
		verbose("Reverting %s" % modu)
		_revert = mh.Module(modu)
		_revertc = _revert.load(main_settings, modules_settings, cfg)
		
		# Revert
		_revertc.revert()
	
	if reboot:
		# We should reboot?
		verbose("KTHXBYE")
		m.sexec("reboot")
	
	sys.exit(0)

