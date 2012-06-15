# -*- coding: utf-8 -*-
# linstaller welcome module frontend - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose,root_check		

class Frontend(glade.Frontend):
	def ready(self):
		# Get text label
		text = self.objects["builder"].get_object("text")
		
		# Format label:
		label = (
			_("Welcome to the %s installation wizard!") % self.moduleclass.main_settings["distro"],
			"",
			_("This wizard will help you with the installation of the distribution into your Hard Disk or another removable media."),
			_("Keep in mind that this installer it's still in testing phase."),
			_("Please report any problem at http://bugs.launchpad.net/linstaller."),
			"",
		)

		# Properly set it
		text.set_markup("\n".join(label))
		
