# globalPlugins\VLCAccessEnhancement\vlc_globalPlugin.py
# a part of vlcAccessEnhancement add-on
# Copyright 2019-2020 paulber19
# This file is covered by the GNU General Public License.


import globalPluginHandler
import addonHandler
import gui
import wx
import ui
import os
import sys

_curAddon = addonHandler.getCodeAddon()
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
import vlc_addonConfig  # noqa:E402
import vlc_settingsHandler  # noqa:E402
from vlc_special import makeAddonWindowTitle  # noqa:E402
del sys.path[-1]

addonHandler.initTranslation()


class VLCGlobalPlugin (globalPluginHandler.GlobalPlugin):
	scriptCategory = _curAddon.manifest["summary"]

	def __init__(self, *args, **kwargs):
		super(VLCGlobalPlugin, self).__init__(*args, **kwargs)
		self.createSubMenu()
		self.vlcrcSettings = vlc_settingsHandler.Vlcrc()
		from . import updateHandler
		vlc_addonConfig.initialize()
		if vlc_addonConfig._addonConfigManager.getAutoUpdateCheck():
			updateHandler.autoUpdateCheck(releaseToDev=vlc_addonConfig._addonConfigManager.getUpdateReleaseVersionsToDevVersions())  # noqa:E501

	def createSubMenu(self):
		self.prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
		menu = wx.Menu()
		self.vlcSettingsMenu = self.prefsMenu .AppendSubMenu(
			menu,
			# Translators: label of the add-on settings menu.
			makeAddonWindowTitle(_("settings ...")),
			# Translators: the tooltip text for addon submenu.
			makeAddonWindowTitle(_("Settings menu")))
		settingsSubMenu = menu.Append(
			wx.ID_ANY,
			# Translators: name of the option in the menu.
			_("Settings") + "...",
			"")
		gui.mainFrame.sysTrayIcon.Bind(
			wx.EVT_MENU, self.onSettingsMenu, settingsSubMenu)
		vlcConfigSubMenu = menu.Append(
			wx.ID_ANY,
			# Translators: name of the option in the menu.
			_("VLC's configuration") + "...",
			"")
		gui.mainFrame.sysTrayIcon.Bind(
			wx.EVT_MENU, self.onVLCConfigMenu, vlcConfigSubMenu)

	def terminate(self):
		try:
			self.preferencesMenu.Remove(self.vlc)
		except:  # noqa:E722
			pass
		super(VLCGlobalPlugin, self).terminate()

	def onSettingsMenu(self, evt):
		from .vlc_configGui import AddonSettingsDialog
		gui.mainFrame._popupSettingsDialog(AddonSettingsDialog)

	def onVLCConfigMenu(self, evt):
		from .vlc_configGui import VLCConfigurationDialog
		gui.mainFrame._popupSettingsDialog(VLCConfigurationDialog)

	def script_activateVLCSettingsDialog(self, gesture):
		self.onSettingsMenu(None)

	# Translators: message presented in input mode.
	script_activateVLCSettingsDialog.__doc__ = _("Display the settings dialog ")

	def script_VLCGlobalPluginTest(self, gesture):
		print("test VLCGlobalPluginTest")
		ui.message("VLCGlobalPluginTest")
		import globalVars
		from .updateHandler.update_check import CheckForAddonUpdate
		fileName = os.path.join(globalVars.appArgs.configPath, "myAddons.latest")
		wx.CallAfter(
			CheckForAddonUpdate, None, updateInfosFile=fileName, silent=False)
	__gestures = {
		"kb:alt+control+f11": "VLCGlobalPluginTest",
		}
