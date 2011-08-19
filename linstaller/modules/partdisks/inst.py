# -*- coding: utf-8 -*-
# linstaller partdisks module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.cli_frontend as cli
import linstaller.core.module as module
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose
import linstaller.core.libmodules.partdisks.library as lib

import os

class Module(module.Module):
	def start(self):
		""" Start override to unsquash. """
		
		# Mount root partition.
		root = self.modules_settings["partdisks"]["root"]
		
		# Ensure that is unmounted
		if os.path.ismount("/linstaller/target"):
			# Target mounted. Unmount
			lib.umount(path="/linstaller/target")
		if lib.is_mounted(root):
			# Partition mounted. Unmount
			lib.umount(path=root)
		
		# Then mount at TARGET
		lib.mount_partition(path=root, target="/linstaller/target")
		
		# Mount every partition which has "useas" on it
		# Get changed.
		changed = self.modules_settings["partdisks"]["changed"]

		used = []

		for key, value in changed.items():
			if not "useas" in value["changes"]:
				# There isn't "useas" in changes; skipping this item
				continue
			
			# Get useas
			useas = value["changes"]["useas"]
			
			if useas in ("/","swap"):
				# Root or swap, do not use it
				continue
			
			# Create mountpoint
			mountpoint = "/linstaller/target" + useas # useas begins with a /, so os.path.join doesn't work
			os.makedirs(mountpoint)
			
			# Mount key to mountpoint
			if lib.is_mounted(key):
				# Umount
				lib.umount(path=key)
			lib.mount_partition(path=key, target=mountpoint)
			
			# Ok, it is mounted. Now let's see if it is empty
			count = len(os.listdir(mountpoint))
			drop = False
			if count == 1:
				# The only one file may be lost+found
				if not os.listdir(mountpoint)[0] == "lost+found":
					# It isn't.
					drop = True # We cannot use it
			elif count > 1:
				# More than one file detected. We cannot use the partition at this stage.
				drop = True
			
			if drop:
				# Umount partition, remove mountpoint
				lib.umount(path=key)
				os.rmdir(mountpoint)
			else:
				# Partition will be used during unsquash, we should remember when linstaller will execute revert
				used.append(key)
		
		# Store used
		self.settings["used"] = used
			

	def revert(self):
		""" Umounts TARGET. """
		
		# Ensure that is mounted
		if not os.path.ismount("/linstaller/target"):
			# Umounted. pass.
			pass
		
		# See if "used" was... used :)
		if "partdisks.inst" in self.modules_settings and "used" in self.modules_settings["partdisks.inst"]:
			_used = self.modules_settings["partdisks.inst"]["used"]
			if _used:
				for part in _used:
					if lib.is_mounted(part):
						lib.umount(path=part)
		
		# Umount target, finally.
		lib.umount(path="/linstaller/target")
	
	def seedpre(self):
		""" Cache settings """
		
		self.cache("used")