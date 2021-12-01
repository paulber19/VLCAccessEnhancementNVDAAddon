# shared\vlc_localeSettingsHandler.py.
# a part of vlcAccessEnhancement add-on
# Copyright 2018-2020 paulber19
# This file is covered by the GNU General Public License.


import addonHandler
import os
from logHandler import log
from configobj import ConfigObj
from languageHandler import getLanguage
import sys

_curAddon = addonHandler.getCodeAddon()
debugToolsPath = os.path.join(_curAddon.path, "debugTools")
sys.path.append(debugToolsPath)
try:
	from debug import printDebug
except ImportError:
	def printDebug(msg): return
del sys.path[-1]


addonHandler.initTranslation()


class LocaleSettings(object):
	def __init__(self):
		curAddon = addonHandler.getCodeAddon()
		self.addonDir = curAddon.path
		localeSettingsFile = self.getLocaleSettingsIniFilePath()
		if localeSettingsFile is None:
			printDebug("LocaleSettings __init__ :Default config")
			self.conf = None
		else:
			self.conf = ConfigObj(
				localeSettingsFile, encoding="utf-8", list_values=False)
		self.loadScriptGestures()

	def getLocaleSettingsIniFilePath(self):
		settingsIniFileName = "settings.ini"
		lang = getLanguage()
		settingsIniFilePath = os.path.join(
			self.addonDir, "locale", getLanguage(), settingsIniFileName)
		if not os.path.exists(settingsIniFilePath):
			lang = getLanguage().split("_")[0]
			settingsIniFilePath = os.path.join(
				self.addonDir, "locale", lang, settingsIniFileName)
			if not os.path.exists(settingsIniFilePath):
				log.warning("No settingsIniFile %s for %s" % (settingsIniFilePath, getLanguage()))  # noqa:E501
				settingsIniFilePath = None

		return settingsIniFilePath

	def loadScriptGestures(self):
		conf = self.conf
		defaultScriptGestures = {
			"goToTime": "kb:control+;",
			"reportElapsedTime": "kb:;",
			"reportRemainingTime": "kb:,",
			"reportTotalTime": "kb:.",
			"reportCurrentSpeed": "kb:/",
			"recordResumeFile": "kb:nvda+control+f5",
			"resumePlayback": "kb:nvda+control+f6",
			"continuePlayback": "kb:alt+control+r",
			"hideShowMenusView": "kb:control+h",
			"adjustmentsAndEffects": "kb:control+e",
			}
		self.scriptGestures = defaultScriptGestures.copy()
		if (conf is None) or ("script-gestures" not in conf.sections):
			printDebug("loadScriptGestures: Default script gestures assignment loaded")
			return
		section = conf["script-gestures"]
		for scriptName in defaultScriptGestures:
			if scriptName in section:
				self.scriptGestures[scriptName] = section[scriptName]
		printDebug("loadScriptGestures: script gestures assignment loaded")

	def getVLCKeysToUpdate(self):
		conf = self.conf
		sectionName = "vlc-assignements"
		if conf is None or sectionName not in conf:
			return None
		return conf[sectionName].copy() if len(conf[sectionName]) else None
