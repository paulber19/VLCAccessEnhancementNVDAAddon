# shared/vlcStrings.py.
# a part of VLC media player add-on
# Copyright 2018 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
from logHandler import log
import os
from configobj import ConfigObj, ConfigObjError
# ConfigObj 5.1.0 and later integrates validate module.
try:
	from configobj.validate import Validator, VdtTypeError
except ImportError:
	from validate import Validator, VdtTypeError
from py3Compatibility import importStringIO
StringIO = importStringIO()
import api
import winUser
from NVDAObjects.IAccessible import getNVDAObjectFromEvent
from IAccessibleHandler import accessibleObjectFromEvent, accNavigate
from oleacc import *
import  ctypes
from NVDAObjects.IAccessible import getNVDAObjectFromEvent
import sys
_curAddon = addonHandler.getCodeAddon()
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
from vlcSettingsHandler import *
#from appModuleDebug import printDebug
def printDebug(str):  return
del sys.path[-1]


# this file manage  necessary strings to recognize some objects depending of vlc language.
# this strings must be defined in strings-xx.ini file for each vlc language.
# this files are placed in vlcLocale folder.

# main section
ID_LanguageName = "LanguageName"
ID_StringToFindLanguage = "StringToFindLanguage"

# for vlc module
# base title  of main window
ID_VLCAppTitle = "VLCAppTitle"
# play button description:  second  child of third border object of first client object
ID_PlayButtonDescription = "PlayButtonDescription"
# pauseThePlayback button description:  child of third border object of first client object
ID_PauseThePlaybackButtonDescription = "PauseThePlaybackButtonDescription"
# unMute image description :first child of client object.
ID_UnMuteImageDescription = "UnMuteImageDescription"
		# normal|loop|repeat check button description
ID_LoopCheckButtonDescription = "LoopCheckButtonDescription"
# Random check button description
ID_RandomCheckButtonDescription = "RandomCheckButtonDescription"
# singleton to store all strings dictionnaries
_stringsDics  = None

#confspec definitions
SCTN_Main = "Main"
SCTN_VLC = "vlc.py".split(".")[0]

mainSection = """
[{main}]
{LanguageName} = string(default = "en")
{StringToFindLanguage} = string(default = "Playback Alt+l")
""".format(main = SCTN_Main, LanguageName = ID_LanguageName,StringToFindLanguage = ID_StringToFindLanguage)

_playButtonDefaultDescription = """Play\nif the playlist is empty, open a medium"""

_vlcSection = """
[{module}]
{vlcAppTitle} = string(default = "VLC media player")
{playButtonDescription} =string(default = {playDefault})
{pauseThePlaybackButtonDescription} = string(default = "Pause the playback")
{unMute} = string(default = "Unmute")
{loopCheckButtonDescription} = string(default = "Click to toggle between loop all, loop one and no loop")
{randomCheckButtonDescription} = string(default = "Random")
""".format(module = SCTN_VLC,vlcAppTitle = ID_VLCAppTitle, playButtonDescription= ID_PlayButtonDescription, playDefault = "", pauseThePlaybackButtonDescription = ID_PauseThePlaybackButtonDescription, unMute = ID_UnMuteImageDescription, loopCheckButtonDescription = ID_LoopCheckButtonDescription, randomCheckButtonDescription = ID_RandomCheckButtonDescription)

_stringsFileBaseName = "strings-"
_stringsIniFilesDirName =  "vlcLocale"


def get_stringsIniFilePath (appLanguage):
	if appLanguage == "":
		return None
	addonDir = addonHandler.getCodeAddon().path
	file = os.path.join(_addonDir, _stringsIniFilesDirName, _stringsFileBaseName + str(appLanguage)+  ".ini")
	if not os.path.exists(file):
		log.error("No strings Ini file: {}".format(file))
		return None
	return file

def getSupportedLanguages():
	printDebug("vlcStrings: getSuppertedLanguages")
	fileList = getStringsIniFilesList()
	supportedLanguages = []
	for file in fileList:
		config = ConfigObj(file, encoding="utf-8" , default_encoding= "ascii")
		sectionName = "Main"
		lang1 = config[sectionName]["LanguageName"]
		temp = file.split("-")[-1]
		lang2 = temp.split(".")[0]
		supportedLanguages.append((lang1,lang2))
	
	
	return supportedLanguages

def _getstringsIniFilesList(stringsFilesDir):
	itemList = os.listdir(stringsFilesDir)
	FilesList = []
	for item in itemList:
		theFile = os.path.join(stringsFilesDir,item)
		if (not os.path.isdir(theFile)
			and os.path.splitext(theFile)[1] == ".ini"
			and _stringsFileBaseName in item
			) :
			FilesList.append(item)
	return FilesList

def _getPlayMenuLabel():
	printDebug ("vlcStrings: _getPlayMenuLabel")
	hdMain=ctypes.windll.user32.GetForegroundWindow()
	try:
		(oIA, childID) = accessibleObjectFromEvent(hdMain, 0,0)

		(o,childID) = accNavigate(oIA,0, NAVDIR_FIRSTCHILD)
		(o,childID) = accNavigate(o,0, NAVDIR_NEXT)
		(o,childID) = accNavigate(o,0, NAVDIR_NEXT)
		(o,childID) = accNavigate(o,0, NAVDIR_FIRSTCHILD)
		(o,childID) = accNavigate(o,0, NAVDIR_FIRSTCHILD)
		(o,childID) = accNavigate(o,0, NAVDIR_NEXT)
		name = o.accName(0).split(" ")[0]
	except:
		log.warning("getPlayMenuLabel: cannot find play menu label")
		name = None
	return name
	
def loadStringsDic():
	global _stringsDics
	printDebug ("loadStringsDic")
	if _stringsDics is not None:
		printDebug ("loadStringsDic: allready loaded")
		return False
	# get label to identify vlc language
	# vlc 3.0 adds shortcut in label but no in vlc 2.x
	playMenuLabel = _getPlayMenuLabel()
	if playMenuLabel is None:
		return False
	printDebug ("loadStringsDic: playMenuLabel = %s" %playMenuLabel)
	printDebug ("loadStringsDic: search vlc language")
	# set path of strings ini files directory
	currAddon = addonHandler.getCodeAddon()
	stringsIniFilesDir = os.path.join(currAddon.path, _stringsIniFilesDirName)
	# get list of all strings ini files
	stringsIniFilesList = _getstringsIniFilesList(stringsIniFilesDir)
	confspec = ConfigObj(StringIO("""
		{main}
		{vlc}
		""".format(main = mainSection, vlc = _vlcSection)
		), list_values=False, encoding="UTF-8")
	confspec.newlines = "\r\n"
	configFileError = None
	val = Validator()
	# search for vlc language
	languageFound =False
	for file in stringsIniFilesList :
		stringsIniFile = os.path.join(stringsIniFilesDir, file)
		try:
			conf = ConfigObj(stringsIniFile, configspec = confspec, indent_type = "\t", encoding="UTF-8")
		except ConfigObjError as e:
			continue
		conf.newlines = "\r\n"
		result = conf.validate(val)
		if not result :
			continue

		if conf[SCTN_Main][ID_StringToFindLanguage] == playMenuLabel:
			# language found
			languageFound =True
			break
	if not languageFound:
		log.warning ("loadStringsDic: no language found")
		return False
	_stringsDics  = conf.copy()
	printDebug ("loadStringsDic: loaded")
	return True
def getString(stringID):
	section ="vlc"
	printDebug("vlcStrings: _getString: section = %s, stringID = %s" %(section, stringID))
	if _stringsDics  is None:
		loadStringsDic()
		if _stringsDics  is None:
			return ""
	if section not in _stringsDics:
		log.warning("getStrings error: not section %s in _stringsDic" %module)
		return""
	dic = _stringsDics [section]
	if not stringID in dic:
		log.warning("getStrings error: not string \"%s\" in dic" %stringID)
		return ""
	return dic[stringID]

def init():
	printDebug("vlcStrings init")
	global _stringsDics
	_stringsDics  = None

