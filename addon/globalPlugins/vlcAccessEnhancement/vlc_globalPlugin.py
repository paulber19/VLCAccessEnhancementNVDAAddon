# globalPlugins\VLCAccessEnhancement\vlc_globalPlugin.py
# a part of vlcAccessEnhancement add-on
# Copyright 2019 paulber19
#This file is covered by the GNU General Public License.


import globalPluginHandler
import addonHandler
addonHandler.initTranslation ()
import gui
from gui import guiHelper
import time
import api
import wx
import speech
import queueHandler
import eventHandler
import ui
_curAddon = addonHandler.getCodeAddon()
_addonSummary = _curAddon.manifest['summary']
import os
import sys
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
import vlc_addonConfig
import vlc_settingsHandler
from vlc_special import makeAddonWindowTitle

del sys.path[-1]


class VLCGlobalPlugin (globalPluginHandler.GlobalPlugin):
	scriptCategory = _addonSummary
	
	def __init__(self, *args, **kwargs):
		super (VLCGlobalPlugin, self).__init__(*args, **kwargs)
		self.createSubMenu ()
		self.vlcrcSettings = vlc_settingsHandler.Vlcrc(_curAddon)
		from . import updateHandler
		vlc_addonConfig.initialize()
		if vlc_addonConfig._addonConfigManager.getAutoUpdateCheck():
			updateHandler.autoUpdateCheck(releaseToDev = vlc_addonConfig._addonConfigManager.getUpdateReleaseVersionsToDevVersions  ())
	
	def createSubMenu (self):
		self.prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
		menu = wx.Menu()
		self.vlcSettingsMenu = self.prefsMenu .AppendSubMenu(menu,
		# Translators:  label of the add-on settings menu.
		makeAddonWindowTitle(_("settings ...")),
			# Translators: the tooltip text for addon submenu.
			makeAddonWindowTitle(_("Settings menu")))
		settingsSubMenu = menu.Append(wx.ID_ANY,
			# Translators: name of the option in the menu.
			_("Settings")+ "...",
			"")
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSettingsMenu, settingsSubMenu)
		
		vlcConfigSubMenu = menu.Append(wx.ID_ANY,
			# Translators: name of the option in the menu.
			_("VLC's configuration")+ "...",
			"")
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onVLCConfigMenu, vlcConfigSubMenu)

	def terminate (self):
		try:
			if wx.version().startswith("4"):
				# for wxPython 4
				self.preferencesMenu.Remove (self.vlc)
			else:
				# for wxPython 3
				self.preferencesMenu.RemoveItem (self.vlc)
		except:
			pass
		super(VLCGlobalPlugin, self).terminate()
	def onSettingsMenu(self, evt):
		from .vlc_configGui import AddonSettingsDialog
		gui.mainFrame._popupSettingsDialog(AddonSettingsDialog)
	def onVLCConfigMenu(self, evt):
		#wx.CallAfter(vlc_addonConfigurationDialog.run)
		from .vlc_configGui import VLCConfigurationDialog
		gui.mainFrame._popupSettingsDialog(VLCConfigurationDialog)

	
	def script_activateVLCSettingsDialog(self, gesture):
		self.onSettingsMenu(None)

	# Translators: message presented in input mode.
	script_activateVLCSettingsDialog.__doc__ = _("Display the settings dialog ")
	#script_activateVLCSettingsDialog.category = _addonSummary
	
	def script_VLCGlobalPluginTest(self, gesture):
		print ("test VLCGlobalPluginTest")
		ui.message("VLCGlobalPluginTest")
		import globalVars
		from .updateHandler.update_check import CheckForAddonUpdate
		fileName= os.path.join(globalVars.appArgs.configPath, "myAddons.latest")
		wx.CallAfter(CheckForAddonUpdate, None, updateInfosFile = fileName, silent = False)	
	__gestures = {
		"kb:alt+control+f11" : "VLCGlobalPluginTest",
		}

