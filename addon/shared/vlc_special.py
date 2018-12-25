# shared/vlc_special.py
# a part of VLC media player add-on
# Copyright 2018 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()
from logHandler import log
import gui
import config
import wx
def makeAddonWindowTitle(dialogTitle):
	curAddon = addonHandler.getCodeAddon()
	addonSummary = curAddon.manifest['summary']
	return  _("{addonSummary}'s add-on - {dialogTitle}").format(addonSummary = addonSummary, dialogTitle = dialogTitle)


def messageBox(message, caption=wx.MessageBoxCaptionStr, style=wx.OK | wx.CENTER, parent=None):
	option = config.conf["presentation"]["reportObjectDescriptions"]
	config.conf["presentation"]["reportObjectDescriptions"] = True
	ret = gui.messageBox(message, caption, style, parent)
	config.conf["presentation"]["reportObjectDescriptions"] = option
	return ret
