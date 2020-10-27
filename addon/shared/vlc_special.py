# shared\vlc_special.py
# a part of vlcAccessEnhancement add-on
# Copyright 2018-2020 paulber19
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


def messageBox(
	message,
	caption=wx.MessageBoxCaptionStr,
	style=wx.OK | wx.CENTER,
	parent=None):
	option = config.conf["presentation"]["reportObjectDescriptions"]
	config.conf["presentation"]["reportObjectDescriptions"] = True
	ret = gui.messageBox(message, caption, style, parent)
	config.conf["presentation"]["reportObjectDescriptions"] = option
	return ret
