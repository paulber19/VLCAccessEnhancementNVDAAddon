# shared\vlc_addonConfig.py
# a part of vlcAccessEnhancement add-on
# Copyright 2019-2021 paulber19
# This file is covered by the GNU General Public License.

# Manages add-on configuration.

import addonHandler
import os
from logHandler import log
import globalVars
import wx
import shutil
from vlc_settingsHandler import QTInterface
from vlc_utils import getTimeString
from vlc_special import makeAddonWindowTitle, messageBox
from configobj import ConfigObj
from configobj.validate import Validator, VdtTypeError
from io import StringIO

addonHandler.initTranslation()
_curAddon = addonHandler.getCodeAddon()

# config section
SCT_General = "General"
SCT_Options = "Options"
SCT_ResumeFiles = "ResumeFiles"

# general section items
ID_ConfigVersion = "ConfigVersion"
ID_SubstractTime = "SubstractTime"
ID_AutoUpdateCheck = "AutoUpdateCheck"
ID_UpdateReleaseVersionsToDevVersions = "UpdateReleaseVersionsToDevVersions"
# options section items
ID_AutoVolumeLevelReport = "AutoVolumeLevelReport"
ID_AutoElapsedTimeReport = "AutoElapsedTimeReport"
ID_PlaybackControlsAccess = "PlaybackControlsAccess"


class AddonConfigManager(object):
	_generalConfSpec = """[{section}]
	{version} = string(default="1.0")
	{autoUpdateCheck} = boolean(default=True)
	{updateReleaseVersionsToDevVersions} = boolean(default=False)
	{substractTime} = string(default="5")
	""".format(
		section=SCT_General,
		version=ID_ConfigVersion,
		autoUpdateCheck=ID_AutoUpdateCheck,
		updateReleaseVersionsToDevVersions=ID_UpdateReleaseVersionsToDevVersions,
		substractTime=ID_SubstractTime)

	_optionsConfSpec = """[{section}]
	{AutoVolumeLevelReport} = boolean(default=True)
	{AutoElapsedTimeReport} = boolean(default=True)
	{playbackControlsPanelAccess} = boolean(default=True)
	""".format(
		section=SCT_Options,
		AutoVolumeLevelReport=ID_AutoVolumeLevelReport,
		AutoElapsedTimeReport=ID_AutoElapsedTimeReport,
		playbackControlsPanelAccess=ID_PlaybackControlsAccess)

	_resumeFilesConfSpec = """[{section}]
""".format(section=SCT_ResumeFiles)

	def __init__(self, vlcSettings):
		self.addon = _curAddon
		self.vlcSettings = vlcSettings
		self._conf = None
		self._configFileError = None
		self._val = Validator()
		self._importOldSettings()
		self._load()
		self._updateResumeFiles()

	def _importOldSettings(self):
		oldConfigFile = os.path.join(self.addon.path, "addonConfig_old.ini")
		if not os.path.isfile(oldConfigFile):
			return
		try:
			shutil.copy(
				oldConfigFile,
				os.path.join(
					globalVars.appArgs.configPath,
					"%sAddon.ini" % self.addon.manifest["name"]))
			os.remove(oldConfigFile)
		except:  # noqa:E722
			log.warning("Cannot import old settings")

	def _load(self):
		confspec = ConfigObj(StringIO(
			"""#{0} add-on Configuration File
{1}
{2}
{3}
			""".format(
				_curAddon .manifest["name"],
				self._generalConfSpec,
				self._optionsConfSpec,
				self._resumeFilesConfSpec)
		), list_values=False, encoding="UTF-8")
		confspec.newlines = "\r\n"
		configFile = os.path.join(
			globalVars.appArgs.configPath, "%sAddon.ini" % self.addon.manifest["name"])
		try:
			self._conf = ConfigObj(
				configFile, configspec=confspec, indent_type="\t", encoding="UTF-8")
		except:  # noqa:E722
			self._conf = ConfigObj(
				None, configspec=confspec, indent_type="\t", encoding="UTF-8")
			self._configFileError = "Error parsing configuration file: %s" % e
		self._conf.newlines = "\r\n"
		result = self._conf.validate(self._val)
		if not result or self._configFileError:
			log.warn(configFileError)
			return
		if not os.path.exists(configFile):
			self.save()

	def _updateResumeFiles(self):
		resumeFiles = self._conf[SCT_ResumeFiles]
		QTI = QTInterface()

		recents = QTI.recents
		change = False
		for f in resumeFiles:
			if f in recents:
				continue
			del resumeFiles[f]
			change = True
		if change:
			self.save()

	def getAltRTime(self, mediaName):
		QTI = QTInterface()
		try:
			return QTI.recents[mediaName]
		except:  # noqa:E722
			return None

	def save(self):
		# Saves the configuration to the config file.
		# We never want to save config if runing securely
		if globalVars.appArgs.secure:
			return
		if self._configFileError:
			raise RuntimeError("config file errors still exist")
		try:
			# Copy default settings and formatting.
			self._conf.validate(self._val, copy=True)
		except VdtTypeError:
			# error in configuration file
			log.warning("saveSettings: validator error: %s" % self._conf.errors)
			return
		try:
			self._conf.write()
		except:  # noqa:E722
			log.warning("Could not save configuration - probably read only file system")

	def getFullFilePath(self):
		# current full file path is the first item in recent files
		QTI = QTInterface()
		firstRecentFile = QTI.firstRecentFile
		return firstRecentFile

	def recordFileToResume(self, resumeTime):
		currentFileName = self.getFullFilePath()
		if currentFileName in self._conf[SCT_ResumeFiles]:
			# Translators: Message shown to ask user to modify resume time.
			msg = _("Do you want to modify resume time for this media ?")
			# Translators: title of message box
			title = makeAddonWindowTitle(_("Confirmation"))
			res = messageBox(msg, title, wx.OK | wx.CANCEL)
			if res == wx.CANCEL:
				return False
		self._conf[SCT_ResumeFiles][currentFileName] = getTimeString(resumeTime)
		self.save()
		return True

	def getResumeFileTime(self):
		currentFileName = self.getFullFilePath()
		if currentFileName not in self._conf[SCT_ResumeFiles]:
			return None
		return self._conf[SCT_ResumeFiles][currentFileName]

	def toggleOption(self, sct, id, toggle=True):
		conf = self._conf
		if toggle:
			conf[sct][id] = not conf[sct][id]
			self.save()
		return conf[sct][id]

	def getAutoUpdateCheck(self):
		return self.toggleOption(SCT_General, ID_AutoUpdateCheck, False)

	def getUpdateReleaseVersionsToDevVersions(self):
		return self.toggleOption(
			SCT_General, ID_UpdateReleaseVersionsToDevVersions, False)

	def toggleAutoUpdateCheck(self):
		return self.toggleOption(SCT_General, ID_AutoUpdateCheck, True)

	def toggleUpdateReleaseVersionsToDevVersions(self):
		return self.toggleOption(
			SCT_General, ID_UpdateReleaseVersionsToDevVersions, True)

	def getAutoVolumeLevelReportOption(self):
		return self.toggleOption(SCT_Options, ID_AutoVolumeLevelReport, False)

	def getAutoElapsedTimeReportOption(self):
		return self.toggleOption(SCT_Options, ID_AutoElapsedTimeReport, False)

	def getPlaybackControlsAccessOption(self):
		return self.toggleOption(SCT_Options, ID_PlaybackControlsAccess, False)

	def toggleAutoVolumeLevelReportOption(self):
		return self.toggleOption(SCT_Options, ID_AutoVolumeLevelReport, True)

	def toggleAutoElapsedTimeReportOption(self):
		return self.toggleOption(SCT_Options, ID_AutoElapsedTimeReport, True)

	def togglePlaybackControlsAccessOption(self):
		return self.toggleOption(SCT_Options, ID_PlaybackControlsAccess, True)


def initialize(vlcSettings=None):
	global _addonConfigManager
	_addonConfigManager = AddonConfigManager(vlcSettings)


_addonConfigManager = None
