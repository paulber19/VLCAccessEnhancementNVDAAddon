# shared/localeSettingsHandler.py.
# a part of VLC media player add-on
# Copyright 2018 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.


import addonHandler
addonHandler.initTranslation()
import os
from logHandler import log
_curAddon = addonHandler.getCodeAddon()
import sys
debugToolsPath = os.path.join(_curAddon.path, "debugTools")
sys.path.append(debugToolsPath)
try:
	from debug import printDebug
except ImportError:
	def printDebug (msg): return
del sys.path[-1]
from configobj import ConfigObj, DuplicateError
import wx
from languageHandler import curLang

class LocaleSettings(object):
	def __init__(self):
		curAddon = addonHandler.getCodeAddon()
		self.addonDir = curAddon.path
		localeSettingsFile = self.getLocaleSettingsIniFilePath()
		if localeSettingsFile is None:
			printDebug("LocaleSettings __init__ :Default config")
			self.conf = None
		else:
			self.conf = ConfigObj(localeSettingsFile, encoding = "utf-8", list_values= False)
		self.loadScriptGestures()
	
	def getLocaleSettingsIniFilePath(self):
		from languageHandler import curLang
		settingsIniFileName = "settings.ini"
		settingsIniFilePath = os.path.join(self.addonDir,"locale",curLang, settingsIniFileName)
		if not os.path.exists(settingsIniFilePath):
			lang = curLang.split("_")[0]
			settingsIniFilePath = os.path.join(self.addonDir,"locale",lang, settingsIniFileName)
			if not os.path.exists(settingsIniFilePath):
				log.warning("No settingsIniFile %s for %s" %(settingsIniFilePath,curLang))
				settingsIniFilePath = None

		return settingsIniFilePath
	
	def loadScriptGestures(self, ):
		conf = self.conf
		defaultScriptGestures = {
			"goToTime" : "kb:control+;",
			"reportElapsedTime" : "kb:;", 
			"reportRemainingTime" : "kb:,",
			"reportTotalTime" : "kb:.",
			"reportCurrentSpeed" : "kb:/",
			"recordResumeFile":"kb:nvda+control+f5",
			"resumePlayback":"kb:nvda+contronl+f6",
			"continuePlayback": "kb:alt+control+r",
			}
		self.scriptGestures = defaultScriptGestures.copy()
		if (conf is None)   or ("script-gestures" not in conf.sections):
			printDebug("loadScriptGestures: Default script gestures assignment loaded")
			return
		section = conf["script-gestures"]
		for scriptName in defaultScriptGestures:
			if scriptName in section:
				self.scriptGestures[scriptName] = section[scriptName]
		printDebug ("loadScriptGestures: script gestures assignment loaded")
	def getVLCKeysToUpdate(self):
		conf = self.conf
		sectionName = "vlc-assignements"
		if conf is  None or sectionName not in conf:
			return None
		return conf[sectionName].copy() if len(conf[sectionName]) else None
		