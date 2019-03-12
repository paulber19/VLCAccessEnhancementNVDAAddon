# install.py
# a part of VLC media player add-on
# Copyright 2018 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()

def uninstallPreviousVersion():
	for addon in addonHandler.getAvailableAddons():
		if addon.manifest["name"] == "vlc" and addon.manifest["author"] == "Daniel Poiraud, PaulBer19":
			addon.requestRemove()
			break

def onInstall():
	import os
	import shutil
	import globalVars
	import gui
	import wx
	# add-on name has  changed. We must uninstall previous version.
	uninstallPreviousVersion()
	previousVersionAddonConfigFile = os.path.join(globalVars.appArgs.configPath, "VLCAddon.ini")
	addonConfigFile = os.path.join(globalVars.appArgs.configPath, "VLCAccessEnhancement.ini")
	for fileName in ["VLCAccessEnhancementAddon.ini", "VLCAddon.ini" ]:
		f= os.path.join(globalVars.appArgs.configPath, fileName)
		if not os.path.isfile(f):
			continue
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_("Do you want to keep current add-on settings ?"),
			# Translators: the title of a message box dialog.
			_("VLC add-on installation"),
			wx.YES|wx.NO|wx.ICON_WARNING)==wx.YES:
			try:
				path = os.path.join(os.path.dirname(__file__).decode("mbcs"), "appModules", "vlc","AddonConfig_old.ini")
				shutil.copy(f, path)
				os.remove(f)
			except:
				pass
		break
def deleteAddonConfig():
	import os
	import globalVars
	from logHandler import log
	configFile = os.path.join(globalVars.appArgs.configPath, "VLCAccessEnhancementAddon.ini")
	if not os.path.exists(configFile):
		return
		
	os.remove(configFile )
	if os.path.exists(configFile):
		log.warning("Error on deletion of VLC addon settings file")
		
	
def onUninstall():
	deleteAddonConfig(  )

