# shared\vlc_special.py
# a part of vlcAccessEnhancement add-on
# Copyright 2018-2025 paulber19
# This file is covered by the GNU General Public License.

import addonHandler
import gui
import config
import wx

addonHandler.initTranslation()


def makeAddonWindowTitle(dialogTitle):
	curAddon = addonHandler.getCodeAddon()
	addonSummary = curAddon.manifest['summary']
	return "%s - %s" % (addonSummary, dialogTitle)
