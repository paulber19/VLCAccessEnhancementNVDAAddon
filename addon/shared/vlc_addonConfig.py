# shared\vlc_addonConfig.py
# a part of vlcAccessEnhancement add-on
# Copyright 2019-2022 paulber19
# This file is covered by the GNU General Public License.

# Manages add-on configuration.

import addonHandler
import os
from logHandler import log
import globalVars
import wx
import gui
import config
from vlc_settingsHandler import QTInterface
from vlc_utils import getTimeString
from vlc_special import makeAddonWindowTitle, messageBox
from configobj import ConfigObj
from configobj.validate import Validator, ValidateError
from io import StringIO

addonHandler.initTranslation()

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

_curAddon = addonHandler.getCodeAddon()
_addonName = _curAddon.manifest["name"]


class BaseAddonConfiguration(ConfigObj):
	_version = ""
	""" Add-on configuration file. It contains metadata about add-on . """
	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = " ")
	""".format(
		section=SCT_General,
		idConfigVersion=ID_ConfigVersion)

	configspec = ConfigObj(StringIO("""# addon Configuration File
	{general}""".format(general=_GeneralConfSpec, )
	), list_values=False, encoding="UTF-8")

	def __init__(self, input):
		""" Constructs an L{AddonConfiguration} instance from manifest string data
		@param input: data to read the addon configuration information
		@type input: a fie-like object.
		"""
		super(BaseAddonConfiguration, self).__init__(
			input, configspec=self.configspec, encoding='utf-8', default_encoding='utf-8')
		self.newlines = "\r\n"
		self._errors = []
		val = Validator()
		result = self.validate(val, copy=True, preserve_errors=True)
		if type(result) == dict:
			self._errors = self.getValidateErrorsText(result)
		else:
			self._errors = None

	def getValidateErrorsText(self, result):
		textList = []
		for name, section in result.items():
			if section is True:
				continue
			textList.append("section [%s]" % name)
			for key, value in section.items():
				if isinstance(value, ValidateError):
					textList.append(
						'key "{}": {}'.format(
							key, value))
		return "\n".join(textList)

	@property
	def errors(self):
		return self._errors


class AddonConfiguration10(BaseAddonConfiguration):
	_version = "1.0"
	_GeneralConfSpec = """[{section}]
	{configVersion} = string(default = {version})
	{autoUpdateCheck} = boolean(default=True)
	{updateReleaseVersionsToDevVersions} = boolean(default=False)
	""".format(
		section=SCT_General,
		configVersion=ID_ConfigVersion,
		version=_version,
		autoUpdateCheck=ID_AutoUpdateCheck,
		updateReleaseVersionsToDevVersions=ID_UpdateReleaseVersionsToDevVersions)

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

	#: The configuration specification
	configspec = ConfigObj(StringIO("""# addon Configuration File
{general}\r\n{options}\r\n{resumeFiles}
""".format(general=_GeneralConfSpec, options=_optionsConfSpec, resumeFiles=_resumeFilesConfSpec)
	), list_values=False, encoding="UTF-8")


class AddonConfigManager(object):
	_currentConfigVersion = "1.0"
	_versionToConfiguration = {
		"1.0": AddonConfiguration10,
	}

	def __init__(self, vlcSettings):
		self.vlcSettings = vlcSettings
		self.configFileName = "%sAddon.ini" % _addonName
		self.loadSettings()
		config.post_configSave.register(self.handlePostConfigSave)
		self._updateResumeFiles()

	def warnConfigurationReset(self):
		wx.CallLater(
			100,
			gui.messageBox,
			# Translators: A message warning configuration reset.
			_(
				"The configuration file of the add-on contains errors. "
				"The configuration has been reset to factory defaults"),
			# Translators: title of message box
			"{addon} - {title}" .format(addon=_curAddon.manifest["summary"], title=_("Warning")),
			wx.OK | wx.ICON_WARNING)

	def loadSettings(self):
		addonConfigFile = os.path.join(
			globalVars.appArgs.configPath, self.configFileName)
		doMerge = True
		if os.path.exists(addonConfigFile):
			# there is allready a config file
			try:
				baseConfig = BaseAddonConfiguration(addonConfigFile)
				if baseConfig.errors:
					e = Exception("Error parsing configuration file:\n%s" % baseConfig.errors)
					raise e
				if baseConfig[SCT_General][ID_ConfigVersion] != self._currentConfigVersion:
					# it's an old config, but old config file must not exist here.
					# Must be deleted
					os.remove(addonConfigFile)
					log.warning(
						"%s: Old configuration version found. Config file is removed: %s" % (_addonName, addonConfigFile))
				else:
					# it's the same version of config, so no merge
					doMerge = False
			except Exception as e:
				log.warning(e)
				# error on reading config file, so delete it
				os.remove(addonConfigFile)
				self.warnConfigurationReset()
				log.warning(
					"%s Addon configuration file error: configuration reset to factory defaults" % _addonName)

		if os.path.exists(addonConfigFile):
			self.addonConfig =\
				self._versionToConfiguration[self._currentConfigVersion](addonConfigFile)
			if self.addonConfig.errors:
				log.warning(self.addonConfig.errors)
				log.warning(
					"%s Addon configuration file error: configuration reset to factory defaults" % _addonName)
				os.remove(addonConfigFile)
				self.warnConfigurationReset()
				# reset configuration to factory defaults
				self.addonConfig =\
					self._versionToConfiguration[self._currentConfigVersion](None)
				self.addonConfig.filename = addonConfigFile
				doMerge = False
		else:
			# no add-on configuration file found
			self.addonConfig =\
				self._versionToConfiguration[self._currentConfigVersion](None)
			self.addonConfig.filename = addonConfigFile
		# merge step
		oldConfigFile = os.path.join(_curAddon.path, self.configFileName)
		if os.path.exists(oldConfigFile):
			if doMerge:
				self.mergeSettings(oldConfigFile)
			os.remove(oldConfigFile)
		if not os.path.exists(addonConfigFile):
			self.saveSettings(True)

	def mergeSettings(self, previousConfigFile):
		baseConfig = BaseAddonConfiguration(previousConfigFile)
		previousVersion = baseConfig[SCT_General][ID_ConfigVersion]
		if previousVersion not in self._versionToConfiguration:
			log.warning("%s: Configuration merge error: unknown previous configuration version number" % _addonName)
			return
		previousConfig = self._versionToConfiguration[previousVersion](previousConfigFile)
		if previousVersion == self.addonConfig[SCT_General][ID_ConfigVersion]:
			# same config version, update data from previous config
			self.addonConfig.update(previousConfig)
			log.warning("%s: Configuration updated with previous configuration file" % _addonName)
			return
		# different config version, so do a  merge with previous config.
		self.addonConfig.mergeWithPreviousConfigurationVersion(previousConfig)
		try:
			# self.addonConfig.mergeWithPreviousConfigurationVersion(previousConfig)
			pass
		except Exception:
			pass

	def _updateResumeFiles(self):
		resumeFiles = self.addonConfig[SCT_ResumeFiles]
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
		except Exception:
			return None

	def saveSettings(self, force=False):
		# We never want to save config if runing securely
		if globalVars.appArgs.secure:
			return
		# We save the configuration, in case the user
			# would not have checked the "Save configuration on exit
			# " checkbox in General settings or force is is True
		if not force and not config.conf['general']['saveConfigurationOnExit']:
			return
		if self.addonConfig is None:
			return
		try:
			val = Validator()
			self.addonConfig.validate(val, copy=True, preserve_errors=True)
			self.addonConfig.write()
			log.warning("%s: configuration saved" % _addonName)
		except Exception:
			log.warning("%s: Could not save configuration - probably read only file system" % _addonName)

	def handlePostConfigSave(self):
		self.saveSettings(True)

	def getFullFilePath(self):
		# current full file path is the first item in recent files
		QTI = QTInterface()
		firstRecentFile = QTI.firstRecentFile
		return firstRecentFile

	def terminate(self):
		self.saveSettings()
		config.post_configSave.unregister(self.handlePostConfigSave)

	def recordFileToResume(self, resumeTime):
		currentFileName = self.getFullFilePath()
		if currentFileName in self.addonConfig[SCT_ResumeFiles]:
			# Translators: Message shown to ask user to modify resume time.
			msg = _("Do you want to modify resume time for this media ?")
			# Translators: title of message box
			title = makeAddonWindowTitle(_("Confirmation"))
			res = messageBox(msg, title, wx.OK | wx.CANCEL)
			if res == wx.CANCEL:
				return False
		self.addonConfig[SCT_ResumeFiles][currentFileName] = getTimeString(resumeTime)
		self.saveSettings(True)
		return True

	def getResumeFileTime(self):
		currentFileName = self.getFullFilePath()
		if currentFileName not in self.addonConfig[SCT_ResumeFiles]:
			return None
		return self.addonConfig[SCT_ResumeFiles][currentFileName]

	def toggleOption(self, sct, id, toggle=True):
		conf = self.addonConfig
		if toggle:
			conf[sct][id] = not conf[sct][id]
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
