# globalPlugins\vlcAccessEnhancement\vlc_configGui.py
# a part of vlcAccessEnhancement add-on
# Copyright 2019- 2021 paulber19
# This file is covered by the GNU General Public License.


import addonHandler
import wx
import gui
from gui.settingsDialogs import SettingsDialog, MultiCategorySettingsDialog, SettingsPanel  # noqa:E501
import os
import sys
_curAddon = addonHandler.getCodeAddon()
path = os.path.join(_curAddon.path, "shared")
sys.path.append(path)
from vlc_addonConfig import _addonConfigManager  # noqa:E402
import vlc_settingsHandler  # noqa:E402
from vlc_special import makeAddonWindowTitle, messageBox  # noqa:E402
del sys.path[-1]

addonHandler.initTranslation()


class VLCOptionsPanel(SettingsPanel):
	# Translators: This is the label for the Options panelg.
	title = _("Options")

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a checkbox in the VLCSettings Dialog.
		labelText = _("Report Automatically &volume's level")
		self.autoVolumeLevelReportCheckBox = sHelper.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.autoVolumeLevelReportCheckBox.SetValue(
			_addonConfigManager.getAutoVolumeLevelReportOption())
		# Translators: This is the label for a checkbox in the VLCSettings dialog.
		labelText = _("Report automatically elapsed &time")
		self.autoElapsedTimeReportCheckBox = sHelper.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.autoElapsedTimeReportCheckBox .SetValue(
			_addonConfigManager.getAutoElapsedTimeReportOption())
		# Translators: This is the label for a checkbox in the VLCSettings dialog.
		labelText = _("Playback &controls's access")
		self.playbackControlsAccessCheckBox = sHelper.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.playbackControlsAccessCheckBox.SetValue(
			_addonConfigManager.getPlaybackControlsAccessOption())

	def postInit(self):
		self.autoVolumeLevelReportCheckBox.SetFocus()

	def saveSettingChanges(self):
		if self.autoVolumeLevelReportCheckBox.IsChecked() != _addonConfigManager .getAutoVolumeLevelReportOption():  # noqa:E501
			_addonConfigManager .toggleAutoVolumeLevelReportOption()
		if self.autoElapsedTimeReportCheckBox .IsChecked() != _addonConfigManager .getAutoElapsedTimeReportOption():  # noqa:E501
			_addonConfigManager .toggleAutoElapsedTimeReportOption()
		if self.playbackControlsAccessCheckBox.IsChecked() != _addonConfigManager .getPlaybackControlsAccessOption():  # noqa:E501
			_addonConfigManager .togglePlaybackControlsAccessOption()

	def postSave(self):
		pass

	def onSave(self):
		self.saveSettingChanges()


class VLCUpdatePanel(SettingsPanel):
	# Translators: This is the label for the Update panel.
	title = _("Update")

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a checkbox in the VLCUpdate Dialog.
		labelText = _("Automatically check for &updates ")
		self.autoCheckForUpdatesCheckBox = sHelper.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.autoCheckForUpdatesCheckBox.SetValue(
			_addonConfigManager.getAutoUpdateCheck())
		# Translators: This is the label for a checkbox in the VLCUpdate dialog.
		labelText = _("Update also release versions to &developpement versions")
		self.updateReleaseVersionsToDevVersionsCheckBox = sHelper.addItem(
			wx.CheckBox(
				self,
				wx.ID_ANY,
				label=labelText))
		self.updateReleaseVersionsToDevVersionsCheckBox.SetValue(
			_addonConfigManager.getUpdateReleaseVersionsToDevVersions())
		# translators: label for a button in VLCUpdate dialog.
		labelText = _("&Check for update")
		checkForUpdateButton = wx.Button(self, label=labelText)
		sHelper.addItem(checkForUpdateButton)
		checkForUpdateButton.Bind(wx.EVT_BUTTON, self.onCheckForUpdate)
		# translators: this is a label for a button in update settings panel.
		labelText = _("View &history")
		seeHistoryButton = wx.Button(self, label=labelText)
		sHelper.addItem(seeHistoryButton)
		seeHistoryButton.Bind(wx.EVT_BUTTON, self.onSeeHistory)

	def onCheckForUpdate(self, evt):
		from .updateHandler import addonUpdateCheck
		self.saveSettingChanges()
		releaseToDevVersion = self.updateReleaseVersionsToDevVersionsCheckBox.IsChecked()  # noqa:E501
		wx.CallAfter(addonUpdateCheck, auto=False, releaseToDev=releaseToDevVersion)
		self.Close()

	def onSeeHistory(self, evt):
		addon = addonHandler.getCodeAddon()
		from languageHandler import curLang
		theFile = os.path.join(addon.path, "doc", curLang, "changes.html")
		if not os.path.exists(theFile):
			lang = curLang.split("_")[0]
			theFile = os.path.join(addon.path, "doc", lang, "changes.html")
			if not os.path.exists(theFile):
				lang = "en"
				theFile = os.path.join(addon.path, "doc", lang, "changes.html")
		os.startfile(theFile)

	def saveSettingChanges(self):
		if self.autoCheckForUpdatesCheckBox.IsChecked() != _addonConfigManager .getAutoUpdateCheck():  # noqa:E501
			_addonConfigManager .toggleAutoUpdateCheck()
		if self.updateReleaseVersionsToDevVersionsCheckBox.IsChecked() != _addonConfigManager .getUpdateReleaseVersionsToDevVersions():  # noqa:E501
			_addonConfigManager .toggleUpdateReleaseVersionsToDevVersions()

	def postSave(self):
		pass

	def onSave(self):
		self.saveSettingChanges()


class VLCConfigurationDialog (SettingsDialog):
	# Translators: The title of the VLC configuration dialog.
	title = makeAddonWindowTitle(_("VLC's configuration"))

	def makeSettings(self, settingsSizer):
		settingsSizerHelper = gui.guiHelper.BoxSizerHelper(
			self,
			sizer=settingsSizer)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		self.modifyVLCShortcutsButton = bHelper.addButton(
			self,
			# Translators: The label of a button
			# to modify vlc shortcuts in the vlc configuration dialog.
			label=_("&Modify vlc shortcuts"))
		self.modifyVLCShortcutsButton.Bind(wx.EVT_BUTTON, self.onModify)

		self.deleteVLCFolder = bHelper.addButton(
			self,
			# Translators: The label of a button
			# to delete vlc configuration folder in VLC configuration dialog.
			label=_("&Delete VLC configuration folder"))
		self.deleteVLCFolder.Bind(wx.EVT_BUTTON, self.onDeleteVLCFolder)
		settingsSizer.Add(bHelper.sizer)

	def postInit(self):
		self.modifyVLCShortcutsButton .SetFocus()

	def onModify(self, evt):
		vlcrc = vlc_settingsHandler.Vlcrc()
		wx.CallLater(100, vlcrc.update)
		self.Destroy()

	def onDeleteVLCFolder(self, evt):
		if messageBox(
			# Translators: message to user
			# to confirm the deletion of VLC configuration folder.
			_("Do you want really to delete VLC configuration folder ?"),
			# Translators: title of message box.
			makeAddonWindowTitle(_("Confirmation")),
			wx.YES | wx.NO) == wx.NO:
			return
		vlc = vlc_settingsHandler.VLCSettings(_curAddon)
		wx.CallLater(100, vlc.deleteConfigurationFolder)
		self.Destroy()


class AddonSettingsDialog(MultiCategorySettingsDialog):
	INITIAL_SIZE = (1000, 480)
	# Min height required to show the OK, Cancel, Apply buttons
	MIN_SIZE = (470, 240)

	categoryClasses = [
		VLCOptionsPanel,
		VLCUpdatePanel
		]

	def __init__(self, parent, initialCategory=None):
		curAddon = addonHandler.getCodeAddon()
		# Translators: title of add-on parameters dialog.
		dialogTitle = _("Settings")
		self.title = "%s - %s" % (curAddon.manifest["summary"], dialogTitle)
		super(AddonSettingsDialog, self).__init__(parent, initialCategory)
