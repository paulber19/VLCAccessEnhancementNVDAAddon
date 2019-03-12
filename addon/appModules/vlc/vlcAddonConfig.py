# appModules/vlc/addonConfig.py.
# a part of VLC media player add-on
# Copyright 2018-2019 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

#Manages add-on configuration.
import addonHandler
addonHandler.initTranslation()
import os
from logHandler import log
import globalVars
import gui
import wx
import api
import speech
import time
import shutil
import sys
_curAddon = addonHandler.getCodeAddon()
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
from vlcUtils import getTimeString
import vlc_special
from  py3Compatibility import importStringIO , _unicode
del sys.path[-1]
from configobj import ConfigObj, ConfigObjError
# ConfigObj 5.1.0 and later integrates validate module.
try:
	from configobj.validate import Validator, VdtTypeError
except ImportError:
	from validate import Validator, VdtTypeError
StringIO = importStringIO ()
# config section
SCT_General = "General"
SCT_ResumeFiles = "ResumeFiles"

# general section items
IT_ConfigVersion= "ConfigVersion"
IT_SubstractTime= "SubstractTime"

class AddonConfigManager(object):
	_generalConfSpec = """[{section}]
	{version} = string(default="1.0")
	{substractTime} = string(default="5")
""".format(section = SCT_General, version = IT_ConfigVersion, substractTime = IT_SubstractTime)
	
	_resumeFilesConfSpec = """[{section}]
""".format(section = SCT_ResumeFiles)
	
	
	def __init__(self,  vlcSettings):
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
			shutil.copy(oldConfigFile, os.path.join(globalVars.appArgs.configPath, "%sAddon.ini"%self.addon.manifest["name"]) )
			os.remove(oldConfigFile)
		except:
			log.warning("Cannot import old settings")
	
	def _load(self):
		confspec = ConfigObj(StringIO(
"""#{0} add-on Configuration File
{1}
{2}
""".format(_curAddon .manifest["name"],self._generalConfSpec, self._resumeFilesConfSpec)
), list_values=False, encoding="UTF-8")
		confspec.newlines = "\r\n"
		configFile = os.path.join(globalVars.appArgs.configPath, "%sAddon.ini"%self.addon.manifest["name"])
		try:
			self._conf = ConfigObj(configFile, configspec = confspec, indent_type = "\t", encoding="UTF-8")
		except:
			self._conf = ConfigObj(None, configspec = confspec, indent_type = "\t", encoding="UTF-8")
			self._configFileError="Error parsing configuration file: %s" %e
		self._conf.newlines = "\r\n"
		result = self._conf.validate(self._val)
		if not result or self._configFileError:
			log.warn(configFileError)
	
	
	def _updateResumeFiles(self):
		sharedPath = os.path.join(self.addon.path, "shared")
		sys.path.append(sharedPath)
		from vlcSettingsHandler import QTInterface 
		del sys.path[-1]
		resumeFiles = self._conf[SCT_ResumeFiles]
		QTInterface = QTInterface (self.addon)
		fileList = []
		for f in QTInterface.recents:
			file = f.split("/")[-1]
			fileList.append(file)
		change = False
		for f in resumeFiles:
			if f in fileList:
				continue
			del resumeFiles[f]
			change = True
		if change:
			self.save()
	
	def getAltRTime(self, mediaName):
		#printDebug ("AddonConfigManager: getAltRTime mediaName = %s"%mediaName)
		sharedPath = os.path.join(self.addon.path, "shared")
		sys.path.append(sharedPath)
		from vlcSettingsHandler import QTInterface 
		del sys.path[-1]
		resumeFiles = self._conf[SCT_ResumeFiles]
		QTInterface = QTInterface (self.addon)
		try:
			return QTInterface.recents[mediaName]
		except:
			return None
	def save(self):
		#Saves the configuration to the config file.
		#We never want to save config if runing securely
		if globalVars.appArgs.secure: return
		if self._configFileError:
			raise RuntimeError("config file errors still exist")
	
		try:
			# Copy default settings and formatting.
			self._conf.validate(self._val, copy = True)
		except VdtTypeError:
			# error in configuration file
			log.warning("saveSettings: validator error: %s"%self._conf.errors )
			return
		try:
			self._conf.write()
		except:
			log.warning("Could not save configuration - probably read only file system")
	
	
	def recordFileToResume(self, fileName, resumeTime):
		if fileName in self._conf[SCT_ResumeFiles]:
			curAddon = addonHandler.getCodeAddon()
			
			# Translators: Message shown to ask user  to modify resume time.
			msg = _("Do you want to modify resume time for this media ?") 
			# TRanslators: title of message box
			title = _("%s - Confirmation")%curAddon.manifest["summary"]
			res = vlc_special.messageBox(msg, title, wx.OK|wx.CANCEL)
			if res== wx.CANCEL:
				return False
		self._conf[SCT_ResumeFiles][fileName] = getTimeString(resumeTime)
		self.save()
		return True
		
	def getResumeFileTime(self, fileName):
		if not fileName in self._conf[SCT_ResumeFiles]:
			return None
		return self._conf[SCT_ResumeFiles][fileName]
