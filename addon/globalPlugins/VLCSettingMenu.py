# globalPlugins/VLCSettingMenu.py
# a part of VLC media player add-on
# Copyright 2018 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

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
import vlcSettingsHandler
import vlc_special

del sys.path[-1]


class GlobalPlugin (globalPluginHandler.GlobalPlugin):
	scriptCategory = _addonSummary
	
	def __init__(self, *args, **kwargs):
		super (GlobalPlugin, self).__init__(*args, **kwargs)
		self.createSubMenu ()
	
	def createSubMenu (self):
		self.preferencesMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
		self.vlc = self.preferencesMenu.Append (wx.ID_ANY,
		# Translators: name of the option in the menu.
			_("%s add-on - settings ...")%_addonSummary, "")
		gui.mainFrame.sysTrayIcon.Bind (wx.EVT_MENU, self.onVLCAddonConfigurationDialog, self.vlc)

	def terminate (self):
		try:
			if wx.version().startswith("4"):
				# for wxPython 4
				self.preferencesMenu.Remove (self.vlc)
			else:
				# for wxPython 3
				self.preferencesMenu.RemoveItem (self.vlc)
		except wx.PyDeadObjectError:
			pass
		super(GlobalPlugin, self).terminate()
	def onVLCAddonConfigurationDialog (self, evt):
		wx.CallAfter(VLCAddonConfigurationDialog.run)
	
	def script_activateVLCAddonConfigurationDialog (self, gesture):
		wx.CallAfter (self.onVLCAddonConfigurationDialog, None)
	# Translators: message presented in input mode.
	script_activateVLCAddonConfigurationDialog.__doc__ = _("Display the add-on 's configuration dialog ")
	script_activateVLCAddonConfigurationDialog.category = _addonSummary
	
	def script_VLCGlobalPluginTest(self, gesture):
		print "test VLCGlobalPluginTest"
		ui.message("VLCGlobalPluginTest")
	
	__gestures = {
		#"kb:alt+control+f11" : "VLCGlobalPluginTest",
		}

class VLCAddonConfigurationDialog (wx.Dialog):
	#class MultiInstanceError(RuntimeError): pass
	
	_hasInstance=False
		# Translators: The title of the add-on configuration dialog box.
	title = _("{0} add-on - settings").format (_addonSummary)
	shouldSuspendConfigProfileTriggers = True

	def __new__(cls, *args, **kwargs):
		if VLCAddonConfigurationDialog ._hasInstance:
			raise VLCAddonConfigurationDialog .MultiInstanceError("Only one instance of SettingsDialog can exist at a time")
		obj = super(VLCAddonConfigurationDialog , cls).__new__(cls, *args, **kwargs)
		VLCAddonConfigurationDialog ._hasInstance=True
		return obj

	def __init__(self, parent):
		super(VLCAddonConfigurationDialog ,self).__init__(parent, wx.ID_ANY, self.title)
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		self.settingsSizer=wx.BoxSizer(wx.VERTICAL)
		self.makeSettings(self.settingsSizer)
		mainSizer.Add(self.settingsSizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Add(wx.StaticLine(self), flag=wx.EXPAND)
		mainSizer.Add(self.CreateButtonSizer(wx.CANCEL), border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL|wx.ALIGN_RIGHT)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.Bind(wx.EVT_BUTTON,self.onCancel,id=wx.ID_CANCEL)
		self.postInit()

	
	def __del__(self):
		VLCAddonConfigurationDialog ._hasInstance=False
	
	def makeSettings (self, settingsSizer):
		settingsSizerHelper = gui.guiHelper.BoxSizerHelper (self, sizer = settingsSizer)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: The label of a button to modify vlc shortcuts in the vlc add-on configuration dialog.
		self.modifyVLCShortcutsButton = bHelper.addButton(self, label=_("&Modify vlc shortcuts"))
		self.modifyVLCShortcutsButton.Bind(wx.EVT_BUTTON, self.onModify)
		# Translators: The label of a button to delete vlc configuration folder.
		self.deleteVLCFolder= bHelper.addButton(self, label= _("&Delete VLC configuration folder"))
		self.deleteVLCFolder.Bind(wx.EVT_BUTTON, self.onDeleteVLCFolder)
		settingsSizer.Add(bHelper.sizer)
	
	def postInit (self):
		self.modifyVLCShortcutsButton .SetFocus()
	
	def onModify(self, evt):
		vlcrc = vlcSettingsHandler.Vlcrc(_curAddon)
		wx.CallLater(100, vlcrc.update)
		self.Destroy()
	def onDeleteVLCFolder(self, evt):
		if vlc_special.messageBox(
			# Translators:  message to ask the user to confirm the deletion of VLC configuration folder.
			_("Do you want really to delete VLC configuration folder ?"),
			# Translators: title of message box.
			_("%s add-on - Confirmation") %_addonSummary,
			wx.YES|wx.NO) == wx.NO:
			return
		vlc = vlcSettingsHandler.VLCSettings(_curAddon)
		wx.CallLater(100, vlc.deleteConfigurationFolder)
		self.Destroy()
		
	def onCancel(self, evt):
		self.Destroy()
	@classmethod
	def run(cls):
		if cls._hasInstance:
			# Translators: the label of a message box dialog.
			msg = _("%s dialog is allready open") %cls.title
			wx.CallLater(2000,queueHandler.queueFunction,queueHandler.eventQueue, speech.speakMessage, msg)
			return
		gui.mainFrame.prePopup()
		d = cls(gui.mainFrame)
		d.CentreOnScreen()
		d.Show()
		gui.mainFrame.postPopup()

