# -*- coding: utf-8 -*-
# linstaller unsquash module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

import time

class Unsquash(glade.Progress):
	def progress(self):
		""" Unsquash the filesystem. """

		self.parent.progress_wait_for_quota()

		filenum = self.parent.progress_quota
		
		self.parent.set_header("hold", _("Uncompressing system"), _("This may take a while."))
		
		verbose("Beginning copying system")
		# Launch unsquashfs
		unsquashfs = self.parent.moduleclass.unsquash.begin()
		
		# Update progressbar
		unsquashfs.process.poll()
		
		self.parent.progress_set_text(_("Uncompressing system..."))
		
		output = [None]
		while unsquashfs.process.poll() == None:
			try:
				toappend = unsquashfs.process.stdout.readline()
				if output[-1] != toappend:
					output.append(toappend)
					
					num = len(output)
					
					# If num > filenum, the progressbar will crash.
					if not num > filenum:
						self.parent.progress_set_percentage(num)
			except:
				# It may fail when resizing the terminal window.
				# This will cause unsync between the progressbar and the unsquashing process.
				# But it's better than let the installer crash ;-)
				pass
			
			#time.sleep(0.2)
		
		if unsquashfs.process.returncode != 0:
			# Write the output into the log file
			for line in output:
				verbose(str(line))
			self.parent.set_header("error", _("An error occoured while uncompressing system to disk."), _("See /var/log/linstaller/linstaller_latest.log for details."))
			self.parent.prepare_for_exit()
			self.quit = False
			
			return
		
		verbose("System copied successfully.")
		
		# Mount.
		verbose("Mounting /proc, /dev and /sys")
		
		self.parent.moduleclass.unsquash.mount()

class Frontend(glade.Frontend):
	def ready(self):
		""" Start the frontend """

		verbose("Calculating the number of the files to copy...")
		filenum = self.moduleclass.unsquash.get_files()
		
		# Set quota
		self.progress_set_quota(filenum)
	
	def process(self):
		""" Start Unsquash() """
		
		clss = Unsquash(self)
		clss.start()
