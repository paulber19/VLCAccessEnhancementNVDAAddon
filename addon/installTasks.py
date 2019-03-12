# install.py
# a part of VLCAcessEnhancement  add-on
# Copyright 2018 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()

previousNameAndAuthor = ("vlc", "Daniel Poiraud, PaulBer19")
previousConfigFileName = "VLCAddon.ini"
curConfigFileName = "VLCAccessEnhancementAddon.ini"
saveConfigFileName = "addonConfig_old.ini"

def uninstallPreviousVersion():
	for addon in addonHandler.getAvailableAddons():
		if (addon.manifest["name"], addon.manifest["author"]) == previousNameAndAuthor:
			addon.requestRemove()
			break

def onInstall():
	import os
	import shutil
	import globalVars
	import gui
	import wx
	import sys
	from logHandler import log
	curPath = os.path.dirname(__file__).decode("mbcs")
	sys.path.append(curPath)
	import buildVars
	addonName = buildVars.addon_info["addon_name"]
	addonSummary = _(buildVars.addon_info["addon_summary"])
	del sys.path[-1]
	# add-on name has  changed. We must uninstall previous version.
	uninstallPreviousVersion()
	# save old configuration
	userConfigPath = globalVars.appArgs.configPath
	curConfigFileName = "%sAddon.ini"%addonName
	for fileName in [curConfigFileName, previousConfigFileName]:
		f= os.path.join(userConfigPath, fileName)
		if not os.path.isfile(f):
			continue
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_("Do you want to keep current add-on settings ?"),
			# Translators: the title of a message box dialog.
			_("%s - installation")%addonSummary,
			wx.YES|wx.NO|wx.ICON_WARNING)==wx.YES:
			try:
				path = os.path.join(curPath, saveConfigFileName )
				shutil.copy(f, path)
				os.remove(f)
			except:
				pass
		break

def deleteAddonConfig():
	import os
	import globalVars
	from logHandler import log
	import sys
	curPath = os.path.dirname(__file__).decode("mbcs")
	sys.path.append(curPath)
	import buildVars
	addonName = buildVars.addon_info["addon_name"]
	del sys.path[-1]
	configFile = os.path.join(globalVars.appArgs.configPath, "%sAddon.ini"%addonName)
	if not os.path.exists(configFile):
		return
	os.remove(configFile )
	if os.path.exists(configFile):
		log.warning("Error on deletion of VLC addon settings file")
	else:
		log.warning("%s file deleted"%configFile)
	
def onUninstall():
	deleteAddonConfig(  )

